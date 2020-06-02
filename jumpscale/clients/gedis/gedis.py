import inspect
import json
import os
import sys
import binascii
from functools import partial

from jumpscale.clients.base import Client
from jumpscale.core.base import fields
from jumpscale.god import j
from jumpscale.servers.gedis.server import GedisErrorTypes, deserialize, serialize, GEDIS_AUTH_CMD
from jumpscale.tools.codeloader import load_python_module
from nacl.public import Box, PublicKey
from nacl.signing import VerifyKey


class ActorResult:
    def __init__(self, **kwargs):
        self.success = kwargs.get("success", True)
        self.result = kwargs.get("result", None)
        self.error = kwargs.get("error", None)
        self.error_type = kwargs.get("error_type", None)
        self.is_async = kwargs.get("is_async", False)
        self.task_id = kwargs.get("task_id", None)

    def __dir__(self):
        return list(self.__dict__.keys())

    def __repr__(self):
        return str(self.__dict__)


class ActorProxy:
    def __init__(self, actor_name, actor_info, client):
        """ActorProxy to remote actor on the server side

        Arguments:
            actor_name {str} -- [description]
            actor_info {dict} -- actor information dict e.g { method_name: { args: [], 'doc':...} }
            gedis_client {GedisClient} -- gedis client reference
        """
        self.actor_name = actor_name
        self.actor_info = actor_info
        self.client = client

    def __dir__(self):
        """Delegate the available functions on the ActorProxy to `actor_info` keys

        Returns:
            list -- methods available on the ActorProxy
        """
        return list(self.actor_info["methods"].keys())

    def __getattr__(self, method):
        """Return a function representing the remote function on the actual actor

        Arguments:
            attr {str} -- method name

        Returns:
            function -- function waiting on the arguments
        """

        def function(*args, **kwargs):
            return self.client.execute(self.actor_name, method, *args, **kwargs)

        func = partial(function)
        func.__doc__ = self.actor_info["methods"][method]["doc"]
        return func


class ActorsCollection:
    def __init__(self, actors):
        self._actors = actors

    def __dir__(self):
        return list(self._actors.keys())

    def __getattr__(self, actor_name):
        if actor_name in self._actors:
            return self._actors[actor_name]


class GedisClient(Client):
    name = fields.String(default="local")
    hostname = fields.String(default="localhost")
    port = fields.Integer(default=16000)
    raise_on_error = fields.Boolean(default=False)
    server_tid = fields.Integer()

    def __init__(self):
        super().__init__()
        self._redisclient = None
        self._loaded_actors = {}
        self._loaded_modules = []
        self.actors = None
        self.explorer = j.clients.explorer.get_default()
        self.identity = j.core.identity
        self.server_tid = self.server_tid or self.identity.tid
        self._auth_server()
        self._load_actors()

    def _get_user_pubkey(self):
        try:
            verify_key = VerifyKey(binascii.unhexlify(self.explorer.users.get(self.server_tid).pubkey))
            return verify_key.to_curve25519_public_key()
        except j.exceptions.NotFound:
            pass

    def _auth_server(self):
        server_pubkey = self._get_user_pubkey()
        box = Box(self.identity.nacl.private_key, server_pubkey)
        data = str(j.data.time.now().timestamp)
        signed_data = self.identity.nacl.signing_key.sign(data.encode())
        encrypted_data = binascii.hexlify(box.encrypt(signed_data)).decode()
        password = j.data.serializers.json.dumps({"threebot_id": self.identity.tid, "encrypted_data": encrypted_data})
        self.execute(GEDIS_AUTH_CMD, password, die=True)

    @property
    def redis_client(self):
        if self._redisclient is None:
            self._redisclient = j.clients.redis.get(name=f"gedis_{self.name}", hostname=self.hostname, port=self.port)
        return self._redisclient

    def _load_module(self, path):
        if path not in self._loaded_modules:
            load_python_module(path)
            self._loaded_modules.append(path)

    def _load_actors(self):
        self._loaded_actors = {}
        for actor_name in self.list_actors():
            actor_info = self._get_actor_info(actor_name)
            self._load_module(actor_info["path"])
            self._loaded_actors[actor_name] = ActorProxy(actor_name, actor_info, self)

        self.actors = ActorsCollection(self._loaded_actors)

    def _get_actor_info(self, actor_name):
        return self.execute(actor_name, "info", die=True).result

    def list_actors(self) -> list:
        """List actors

        Returns:
            list -- List of loaded actors
        """
        return self.execute("core", "list_actors", die=True).result

    def reload(self):
        """Reload actors
        """
        self._redisclient = None
        self._auth_server()
        self._load_actors()

    def execute(self, actor_name: str, actor_method: str, *args, die: bool = False, **kwargs) -> ActorResult:
        """Execute actor's method

        Arguments:
            actor_name {str} -- actor name
            actor_method {str} -- actor method

        Keyword Arguments:
            die {bool} --  flag to raise an error when request fails (default: {False})

        Raises:
            RemoteException: Raises if the request failed and raise_on_error flag is set

        Returns:
            ActorResult -- request result
        """
        payload = json.dumps((args, kwargs), default=serialize)
        response = self.redis_client.execute_command(actor_name, actor_method, payload)
        response = json.loads(response, object_hook=deserialize)

        if not response["success"]:
            if die or self.raise_on_error:
                raise RemoteException(response["error"])

            response["error_type"] = GedisErrorTypes(response["error_type"])

        return ActorResult(**response)


class RemoteException(Exception):
    pass
