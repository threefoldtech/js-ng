import inspect
import json
import os
import sys
from enum import Enum
from functools import partial
from io import BytesIO
from signal import SIGKILL, SIGTERM
from types import ModuleType

import gevent
from gevent import time
from gevent.pool import Pool
from gevent.server import StreamServer
from jumpscale.core.base import Base, fields
from jumpscale.loader import j
from redis import Redis
from redis.connection import DefaultParser, Encoder
from redis.exceptions import ConnectionError

from .baseactor import BaseActor
from .systemactor import CoreActor, SystemActor


def serialize(obj):
    if not isinstance(obj, (str, int, float, list, tuple, dict, bool)):
        module = inspect.getmodule(obj).__file__[:-3]
        return dict(__serialized__=True, module=module, type=obj.__class__.__name__, data=obj.to_dict())
    return obj


def deserialize(obj):
    if isinstance(obj, dict) and obj.get("__serialized__"):
        module = sys.modules[obj["module"]]
        object_instance = getattr(module, obj["type"])()
        object_instance.from_dict(obj["data"])
        return object_instance
    return obj


class GedisErrorTypes(Enum):
    NOT_FOUND = 0
    BAD_REQUEST = 1
    ACTOR_ERROR = 3
    INTERNAL_SERVER_ERROR = 4
    PERMISSION_ERROR = 5


EXCEPTIONS_MAP = {
    j.exceptions.Value: GedisErrorTypes.BAD_REQUEST.value,
    j.exceptions.NotFound: GedisErrorTypes.NOT_FOUND.value,
    j.exceptions.Permission: GedisErrorTypes.PERMISSION_ERROR.value,
}


class RedisConnectionAdapter:
    def __init__(self, sock):
        self.socket = sock
        self._sock = sock
        self.socket_timeout = 600
        self.socket_connect_timeout = 600
        self.socket_keepalive = True
        self.retry_on_timeout = True
        self.socket_keepalive_options = {}
        self.encoder = Encoder("utf", "strict", False)


class ResponseEncoder:
    def __init__(self, socket):
        self.socket = socket
        self.buffer = BytesIO()

    def encode(self, value):
        """Respond with data."""
        if value is None:
            self._write_buffer("$-1\r\n")
        elif isinstance(value, int):
            self._write_buffer(":{}\r\n".format(value))
        elif isinstance(value, bool):
            self._write_buffer(":{}\r\n".format(1 if value else 0))
        elif isinstance(value, str):
            if "\n" in value:
                self._bulk(value)
            else:
                self._write_buffer("+{}\r\n".format(value))
        elif isinstance(value, bytes):
            self._bulkbytes(value)
        elif isinstance(value, list):
            if value and value[0] == "*REDIS*":
                value = value[1:]
            self._array(value)
        elif hasattr(value, "__repr__"):
            self._bulk(value.__repr__())
        else:
            value = j.data.serializers.json.dumps(value, encoding="utf-8")
            self.encode(value)

        self._send()

    def status(self, msg="OK"):
        """Send a status."""
        self._write_buffer("+{}\r\n".format(msg))
        self._send()

    def error(self, msg):
        """Send an error."""
        # print("###:%s" % msg)
        self._write_buffer("-ERR {}\r\n".format(msg))
        self._send()

    def _bulk(self, value):
        """Send part of a multiline reply."""
        data = ["$", str(len(value)), "\r\n", value, "\r\n"]
        self._write_buffer("".join(data))

    def _array(self, value):
        """send an array."""
        self._write_buffer("*{}\r\n".format(len(value)))
        for item in value:
            self.encode(item)

    def _bulkbytes(self, value):
        data = [b"$", str(len(value)).encode(), b"\r\n", value, b"\r\n"]
        self._write_buffer(b"".join(data))

    def _write_buffer(self, data):
        if isinstance(data, str):
            data = data.encode()

        self.buffer.write(data)

    def _send(self):
        self.socket.sendall(self.buffer.getvalue())
        self.buffer = BytesIO()  # seems faster then truncating


SERIALIZABLE_TYPES = (str, int, float, list, tuple, dict, bool)
RESERVED_ACTOR_NAMES = ("core", "system")


class GedisServer(Base):
    host = fields.String(default="127.0.0.1")
    port = fields.Integer(default=16000)
    enable_system_actor = fields.Boolean(default=True)
    run_async = fields.Boolean(default=True)
    actors = fields.Typed(dict, default={}, stored=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._core_actor = CoreActor()
        self._system_actor = SystemActor()
        self.actors["core"] = self._core_actor

    def start(self):
        """Starts the server
        """
        # handle signals
        for signal_type in (SIGTERM, SIGKILL):
            gevent.signal(signal_type, self.stop)

        # register system actor if enabled
        if self.enable_system_actor:
            self.register_actor("system", self._system_actor)

        self._core_actor.set_server(self)
        self._system_actor.set_server(self)

        # start the server
        self._server = StreamServer((self.host, self.port), self._on_connection, spawn=Pool())
        self._server.reuse_addr = True
        self._server.start()

        j.logger.info(f"Gedis server is started at {self.host}:{self.port}...")

    def stop(self):
        """Stops the server
        """
        j.logger.info("Shutting down...")
        self._server.stop()

    def get_and_validate_actor(self, module: ModuleType):
        """
        get and validate actor object from a given module

        Args:
            module (ModuleType): actor module

        Raises:
            j.exceptions.Validation: if the actor is not valid

        Returns:
            BaseActor: actor object
        """
        actor = module.Actor()
        result = actor.__validate_actor__()

        if not result["valid"]:
            raise j.exceptions.Validation(
                "Actor {} is not valid, check the following errors {}".format(actor_name, result["errors"])
            )

        return actor

    def register_actor_module(self, actor_name: str, actor_module: ModuleType):
        actor = self.get_and_validate_actor(actor_module)
        self.register_actor(actor_name, actor)

    def register_actor(self, actor_name: str, actor: BaseActor):
        self.actors[actor_name] = actor

    def unregister_actor(self, actor_name: str):
        self.actors.pop(actor_name, None)

    def _execute(self, method, args, kwargs):
        response = {}
        try:
            response["result"] = method(*args, **kwargs)

        except Exception as e:
            j.logger.exception(f"error while executing {method}", exception=e)

            response["error"] = str(e)
            response["error_type"] = EXCEPTIONS_MAP.get(e.__class__, GedisErrorTypes.ACTOR_ERROR.value)

        return response

    def _on_connection(self, socket, address):
        j.logger.info("New connection from {}", address)
        parser = DefaultParser(65536)
        connection = RedisConnectionAdapter(socket)
        try:
            encoder = ResponseEncoder(socket)
            parser.on_connect(connection)

            while True:
                response = dict(success=True, result=None, error=None, error_type=None, is_async=False, task_id=None)
                try:
                    request = parser.read_response()

                    if len(request) < 2:
                        response["error"] = "invalid request"
                        response["error_type"] = GedisErrorTypes.BAD_REQUEST.value

                    else:
                        actor_name = request.pop(0).decode()
                        method_name = request.pop(0).decode()
                        actor_object = self.actors.get(actor_name)

                        if not actor_object:
                            response["error"] = "actor not found"
                            response["error_type"] = GedisErrorTypes.NOT_FOUND.value

                        elif not hasattr(actor_object, method_name):
                            response["error"] = "method not found"
                            response["error_type"] = GedisErrorTypes.NOT_FOUND.value

                        else:
                            j.logger.info(
                                "Executing method {} from actor {} to client {}", method_name, actor_name, address
                            )

                            if request:
                                args, kwargs = json.loads(request.pop(0), object_hook=deserialize)
                            else:
                                args, kwargs = (), {}

                            method = getattr(actor_object, method_name)
                            result = self._execute(method, args, kwargs)
                            response.update(result)

                except ConnectionError:
                    j.logger.info("Client {} closed the connection", address)

                except Exception as exception:
                    j.logger.exception("internal error", exception=exception)
                    response["error"] = "internal server error"
                    response["error_type"] = GedisErrorTypes.INTERNAL_SERVER_ERROR.value

                response["success"] = response["error"] is None
                encoder.encode(json.dumps(response, default=serialize))

            parser.on_disconnect()

        except BrokenPipeError:
            pass
