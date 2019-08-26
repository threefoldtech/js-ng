from jumpscale.core.base import StoredFactory
from .gogs import Gogs


factory = StoredFactory(Gogs)
