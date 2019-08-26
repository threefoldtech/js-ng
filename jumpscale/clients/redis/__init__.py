from jumpscale.core.base import StoredFactory

from .redis import Redis


factory = StoredFactory(Redis)
