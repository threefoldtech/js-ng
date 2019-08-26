from jumpscale.clients.base import Client
from jumpscale.core.base import fields
from redis import Redis as R


class Redis(Client):
    hostname = fields.String(default="localhost")
    port = fields.Integer(default=6379)

    def __init__(self):
        self.__client = None
        super().__init__()

    @property
    def redis_client(self):
        if not self.__client:
            self.__client = R(self.hostname, self.port)
        return self.__client

    def set(self, k, v):
        return self.redis_client.set(k, v)

    def get(self, k):
        return self.redis_client.get(k)
