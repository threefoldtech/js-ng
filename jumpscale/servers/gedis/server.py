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

def GedisRequestHandler(socket, address):
    print('New connection from {}'.format(address))
    parser = DefaultParser(65536)
    conn = DummyConnection(socket)
    parser.on_connect(conn)
    try:
        while True:
            resp = parser.read_response()
            print(resp)
            conn.socket.sendall(parser.encoder.encode("hi"))
    except Exception as e:
        print(e)
    
    parser.on_disconnect()

    # rfileobj = socket.makefile(mode='rb')

    # rfileobj.close()




def new_server(endpoint=("127.0.0.1", 16000), handler=GedisRequestHandler):
    s = StreamServer(endpoint, handler)
    s.reuse_addr = True
    s.serve_forever()


