from jumpscale.clients.base import Client
from jumpscale.core.base import fields
from jumpscale.god import j
from functools import partial
import json
from typing import List

"""
JS-NG> gedis = j.clients.gedis.get("local")
JS-NG> gedis.list_actors()
['system']

JS-NG> gedis.register_actor("greeter", "/home/ahmed/wspace/js-next/js-ng/jumpscale/servers/gedis/example_greeter.py")
1

JS-NG> gedis.list_actors()
['system', 'greeter']

JS-NG>


JS-NG> gedis.ppdoc("greeter")
{
  "add2": {
    "args": [
      "a",
      "b"
    ],
    "doc": "Add two args\n        \n        "
  },
  "hi": {
    "args": [],
    "doc": "returns hello world\n        "
  },
  "info": {
    "args": [
      "result",
      "members",
      "name",
      "attr"
    ],
    "doc": ""
  },
  "ping": {
    "args": [],
    "doc": "\n        \n        "
  }
}
JS-NG> gedis.execute("greeter", "hi")
b'hello world'

JS-NG> gedis.execute("greeter", "ping")
b'pong no?'

JS-NG> gedis.execute("greeter", "add2", "first", "second")
b'firstsecond'


JS-NG> gedis = j.clients.gedis.get("local")
JS-NG> gedis.actors.greeter.hi()
b'hello world'

JS-NG> gedis.actors.greeter.add2("a", "b")
b'ab'
JS-NG>
"""


class ActorProxy:
    def __init__(self, actor_name, actor_info, gedis_client):
        """ActorProxy to remote actor on the server side

        Arguments:
            actor_name {str} -- [description]
            actor_info {dict} -- actor information dict e.g { method_name: { args: [], 'doc':...} }
            gedis_client {GedisClient} -- gedis client reference
        """
        self.actor_name = actor_name
        self.actor_info = actor_info
        self._gedis_client = gedis_client

    def __dir__(self):
        """Delegate the available functions on the ActorProxy to `actor_info` keys

        Returns:
            list -- methods available on the ActorProxy
        """
        return list(self.actor_info.keys())

    def __getattr__(self, attr):
        """Return a function representing the remote function on the actual actor

        Arguments:
            attr {str} -- method name

        Returns:
            function -- function waiting on the arguments
        """

        def mkfun(actor_name, fn_name, *args):
            return self._gedis_client.execute(self.actor_name, fn_name, *args)

        mkfun.__doc__ = self.actor_info[attr]["doc"]
        return partial(mkfun, self.actor_name, attr)


class ActorsCollection:
    def __init__(self, gedis_client):
        """ActorsCollection to allow using the actors like `gedis.actors.ACTORNAME.ACTORMETHOD(*ACTOR_METHOD_ARGS)

        Arguments:
            gedis_client {GedisClient} -- gedis client
        """
        self._gedis_client = gedis_client
        self._actors = {}

    @property
    def actors_names(self):
        # TODO: CHECK IF WE SHOULD USE CACHE HERE?
        return json.loads(self._gedis_client.execute("system", "list_actors"))

    def __dir__(self):
        return self.actors_names

    def _load_actor(self, actor_name):
        """Load actor: creating ActorProxy for remote actor `actor_name` and store it in the collection.

        Arguments:
            actor_name {str} -- remote actor name

        Returns:
            ActorProxy -- ActorProxy that can call the remote actor.
        """
        actor_info = json.loads(self._gedis_client.execute(actor_name, "info"))
        self._actors[actor_name] = ActorProxy(actor_name, actor_info, self._gedis_client)
        return self._actors[actor_name]

    def __getattr__(self, actor_name):
        if actor_name not in self._actors:
            return self._load_actor(actor_name)
        else:
            return self._actors[actor_name]


class GedisClient(Client):
    name = fields.String(default="local")
    hostname = fields.String(default="localhost")
    port = fields.Integer(default=16000)

    def __init__(self):
        super().__init__()
        self._redisclient = None
        self.redis_client
        self.actors = ActorsCollection(self)

    @property
    def redis_client(self):
        if not self._redisclient:
            try:
                self._redisclient = j.clients.redis.get(f"gedis_{self.name}")
            except:
                self._redisclient = j.clients.redis.new(f"gedis_{self.name}")

        self._redisclient.hostname = self.hostname
        self._redisclient.port = self.port
        self._redisclient.save()
        return self._redisclient

    def register_actor(self, actor_name: str, actor_path: str):
        """Register actor on the server side (gedis server)

        Arguments:
            actor_name {str} -- actor name to be used in the system
            actor_path {str} -- actor path on the remote gedis server

        """
        return self.execute("system", "register_actor", actor_name, actor_path)

    def execute(self, actor_name: str, actor_method: str, *args):
        """Execute

        Arguments:
            actor_name {str} -- actor name
            actor_name {str} -- actor method to execute
            *args      {List[object]}  -- *args of parameters

        """
        return self._redisclient.execute_command(actor_name, actor_method, *args)

    def doc(self, actor_name: str):
        """Gets the documentation of actor `actor_name`

        Arguments:
            actor_name {str} -- actor to retrieve its documentation

        """
        return json.loads(self.execute(actor_name, "info"))

    def ppdoc(self, actor_name):
        """Pretty print documentation of actor

        Arguments:
            actor_name {str} -- actor to print its documentation.
        """
        res = self.doc(actor_name)
        print(json.dumps(res, indent=2, sort_keys=True))

    def list_actors(self) -> List[str]:
        """List actors

        Returns:
            List[str] -- list of actors available on gedis server.
        """
        return json.loads(self.execute("system", "list_actors"))
