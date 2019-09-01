from jumpscale.core.base import StoredFactory

from .redis import RedisClient


module_export_as = StoredFactory(RedisClient)
