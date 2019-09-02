import sys
from io import BytesIO
from functools import partial
import gevent
from gevent import time
from gevent.pool import Pool
from gevent.server import StreamServer
import signal
from redis.connection import DefaultParser, Encoder
from jumpscale.god import j



"""
~>  redis-cli -p 16000 greeter hi              
actor greeter isn't loaded
 ~>  redis-cli -p 16000 system register_actor greeter /home/ahmed/wspace/js-next/js-ng/jumpscale/servers/gedis/example_greeter.py
(integer) -1
 ~>  redis-cli -p 16000 greeter hi              
 hello world
 ~>  redis-cli -p 16000 greeter add2 jo deboeck 
 "jodeboeck"
 ~>  fuser -k 16000/tcp                         

16000/tcp:           29331
 ~>  redis-cli -p 16000 greeter hi              
 actor greeter isn't loaded
 ~>  redis-cli -p 16000 system register_actor greeter /home/ahmed/wspace/js-next/js-ng/jumpscale/servers/gedis/example_greeter.py
(integer) -1
 ~>  redis-cli -p 16000 greeter hi              
 hello world
 ~>  redis-cli -p 16000 greeter ping            

pong no?
 ~>  redis-cli -p 16000 greeter add2 reem khamis
"reemkhamis"
"""

class RedisConnectionAdapter:
    def __init__(self, sock):
        self.socket = sock
        self._sock = sock
        self.socket_timeout = 600
        self.socket_connect_timeout = 600
        self.socket_keepalive = True
        self.socket_keepalive_options = {}
        self.retry_on_timeout = True
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



class GedisServer:
    def __init__(self, endpoint=("127.0.0.1", 16000), actors=None):
        self.actors = actors or {}
        self.endpoint = endpoint

    def start(self):
        s = StreamServer(self.endpoint, self.on_connection)

        gevent.signal(signal.SIGTERM, s.stop)
        gevent.signal(signal.SIGINT, s.stop)
        s.reuse_addr = True
        s.serve_forever()

    def stop(self):
        if self.closed:
            sys.exit('Multiple exit signals received - aborting.')
        else:
            log('Closing listener socket')
            StreamServer.close(self)


    def on_connection(self, socket, address):

        print('New connection from {}'.format(address))
        parser = DefaultParser(65536)
        conn = RedisConnectionAdapter(socket)
        encoder = ResponseEncoder(socket)
        parser.on_connect(conn)
        try:
            while True:
                resp = parser.read_response()
                print(resp)
                if len(resp) > 1:
                    actor_name = resp[0].decode()
                    method_name = resp[1].decode()
                    args = resp[2:]
                    print("SERVICE: {} METHOD: {} ARGS : {} ".format(actor_name, method_name, args))
                    if actor_name not in self.actors:
                        encoder.encode("actor {} isn't loaded".format(actor_name))
                    else:
                        actor = self.actors[actor_name]
                        m = getattr(actor, method_name)
                        res = None
                        res = m(*args)
                        print("RES: ", res)
                        encoder.encode(res)
        except Exception as e:
            # import traceback
            # exc_info = sys.exc_info()
            # traceback.print_exception(*exc_info)
            print(e)
        
        parser.on_disconnect()




class SystemActor:

    def __init__(self, server):
        self.server = server

    def register_actor(self, actor_name, actor_path):
        import importlib
        import os
        import sys

        actor_name = actor_name.decode()
        actor_path = actor_path.decode()

        if actor_name in self.server.actors:
            return True
        module_python_name = os.path.dirname(actor_path)
        module_name = os.path.splitext(module_python_name)[0]
        spec = importlib.util.spec_from_file_location(module_name, actor_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module 
        spec.loader.exec_module(module)
        self.server.actors[actor_name] = module.Actor()
        print(self.server.actors)

        return True

def new_server(actors=None):
    actors = actors or {}
    if not actors:
        print("empty actors on the gedis server.")

    s = GedisServer()
    default_actors = {"system": SystemActor(s)}
    s.actors = {**s.actors, **default_actors}    
    s.start()
    gevent.wait()

