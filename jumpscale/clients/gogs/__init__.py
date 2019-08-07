from jumpscale.clients.base import ClientFactory

from .gogs import Gogs


factory = ClientFactory(Gogs)
