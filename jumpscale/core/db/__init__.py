def export_module_as():

    from jumpscale.god import j
    from redis.exceptions import ConnectionError

    class DefaultRedisDB:
        def __init__(self):
            self._db = None

        @property
        def db(self):
            if not self._db:
                try:
                    self._db = j.clients.redis.get('main')
                    self._db.ping()
                except ConnectionError:
                    j.logger.error("Cannot connect to redis")
            return self._db

    return DefaultRedisDB().db
