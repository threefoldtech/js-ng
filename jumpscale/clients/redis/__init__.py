from jumpscale.core.base import StoredFactory

from .redis import RedisClient


export_module_as = StoredFactory(RedisClient)
