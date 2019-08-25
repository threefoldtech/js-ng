from jumpscale.clients.base import StoredFactory

from .gogs import Gogs


factory = StoredFactory(Gogs)
