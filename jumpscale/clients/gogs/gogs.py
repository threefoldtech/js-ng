from jumpscale.clients.base import Client
from jumpscale.core import fields


class Gogs(Client):
    access_token = fields.String()
