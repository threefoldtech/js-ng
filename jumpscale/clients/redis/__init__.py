from jumpscale.core.base import StoredFactory

from .redis import RedisClient


factory = StoredFactory(RedisClient)
