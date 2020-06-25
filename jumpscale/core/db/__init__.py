def export_module_as():

    from jumpscale.loader import j
    from redis.exceptions import ConnectionError

    class DefaultRedisDB:
        def __init__(self):
            self._db = None

        @property
        def db(self):
            if not self._db:
                self._db = j.clients.redis.get("main")
            return self._db

    return DefaultRedisDB().db
