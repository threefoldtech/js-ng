from jumpscale.clients.base import Client
from jumpscale.core.base import fields


class Gogs(Client):
    access_token = fields.String()
