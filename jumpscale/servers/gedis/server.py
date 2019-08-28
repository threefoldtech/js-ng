from functools import partial
import gevent
from gevent import time
from gevent.pool import Pool
from gevent.server import StreamServer
from redis.connection import DefaultParser, Encoder

class DummyConnection:
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
        self.dirty = False

    def encode(self, value):
        """Respond with data."""
        if isinstance(value, (list, tuple)):
            self._write('*{}\r\n'.format(len(value)))
            for v in value:
                self._bulk(v)
        elif isinstance(value, int):
            self._write(':{}\r\n'.format(value))
        elif isinstance(value, bool):
            self._write(':{}\r\n'.format(1 if value else 0))
        else:
            self._bulk(value)

    def status(self, msg="OK"):
        """Send a status."""
        self._write("+{}\r\n".format(msg))

    def error(self, msg):
        """Send an error."""
        self._write("-{}\r\n".format(msg))

    def _bulk(self, value):
        """Send part of a multiline reply."""
        data = ["$", str(len(value)), "\r\n", str(value), "\r\n"]
        self._write("${}\r\n{}\r\n".format(len(value), value))

    def _write(self, data):
        if not self.dirty:
            self.dirty = True
        if isinstance(data, str):
            data = data.encode('utf-8')
        self.socket.send(data)

def GedisRequestHandler(services, socket, address):
    print('New connection from {}'.format(address))
    parser = DefaultParser(65536)
    conn = DummyConnection(socket)
    encoder = ResponseEncoder(socket)
    parser.on_connect(conn)
    try:
        while True:
            resp = parser.read_response()
            print(resp)
            if len(resp) > 1:
                service = resp[0].decode()
                method = resp[1].decode()
                args = [x.decode() for x in resp[2:]] if len(resp) > 2 else []
                print("SERVICE: {} METHOD: {} ARGS : {} ".format(service, method, args))
                m = getattr(services[service], method)
                res = None
                if args:
                    res = m(*args)
                else:
                    res = m()
                print("RES: ", res)
                encoder.encode(res)
    except Exception as e:
        print(e)
    
    parser.on_disconnect()


class Greeter:
    def hi(self):
        return "hello world"

    def ping(self):
        return "pong no?"

    def add2(self, a, b):
        return a+b


actors = {'greeter': Greeter()}

def new_server(endpoint=("127.0.0.1", 16000), handler=partial(GedisRequestHandler, actors)):
    s = StreamServer(endpoint, handler)
    s.reuse_addr = True
    s.serve_forever()
    # FIXME: add sig handler for INT
    

