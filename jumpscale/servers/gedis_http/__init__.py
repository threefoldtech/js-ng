import json
from jumpscale.core.base import Base, fields
from jumpscale.loader import j
from gevent.pool import Pool
from bottle import Bottle, abort, request, response
from jumpscale.servers.gedis.server import GedisErrorTypes
from gevent.pywsgi import WSGIServer
from jumpscale.core.base import StoredFactory


class GedisHTTPServer(Base):
    host = fields.String(default="127.0.0.1")
    port = fields.Integer(default=8000)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._app = Bottle()
        self._client = None
        self._app.route("/<package>/<actor>/<method>", ["GET", "POST"], self.handler)

    @property
    def client(self):
        if self._client is None:
            self._client = j.clients.gedis.get(self.instance_name)
            self._client.disable_deserialization = True
        return self._client

    def make_response(self, code, content):
        response.status = code
        response.content_type = "application/json"
        return json.dumps(content)

    def handler(self, package, actor, method):
        actors = self.client.actors

        actor = getattr(actors, f"{package}_{actor}", None)
        if not actor:
            return self.make_response(400, {"error": "actor not found"})

        method = getattr(actor, method, None)
        if not method:
            return self.make_response(400, {"error": "method not found"})

        kwargs = request.json or dict()
        response = method(**kwargs)

        if not response.success:
            if response.error_type == GedisErrorTypes.NOT_FOUND:
                return self.make_response(404, {"error": response.error})

            elif response.error_type == GedisErrorTypes.BAD_REQUEST:
                return self.make_response(400, {"error": response.error})

            elif response.error_type == GedisErrorTypes.PERMISSION_ERROR:
                return self.make_response(403, {"error": response.error})

            else:
                return self.make_response(500, {"error": response.error})

        return self.make_response(200, response.result)

    @property
    def gevent_server(self):
        return WSGIServer((self.host, self.port), self._app, spawn=Pool())


def export_module_as():
    return StoredFactory(GedisHTTPServer)
