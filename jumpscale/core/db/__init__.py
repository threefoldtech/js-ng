from jumpscale.god import j
from redis.exceptions import ConnectionError


class DefaultRedisDB:
    def __init__(self):
        self._db = None

    @property
    def db(self):
        if not self._db:
            try:
                self._db = j.clients.redis.get("main")
                self._db.ping()
            except ConnectionError:
                # TODO log
                return None
        return self._db


export_module_as = DefaultRedisDB().db
