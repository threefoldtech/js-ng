def export_module_as():
    from jumpscale.core.base import StoredFactory

    from .redis import RedisClient

    return StoredFactory(RedisClient)
