from jumpscale.clients.base import Client
from jumpscale.core.base import fields
from redis import Redis


class RedisClient(Client):
    hostname = fields.String(default="localhost")
    port = fields.Integer(default=6379)

    def __init__(self):
        self.__client = None
        super().__init__()

    def __dir__(self):
        return list(self.__dict__.keys()) + dir(self.redis_client)
    
    @property
    def redis_client(self):
        if not self.__client:
            self.__client = Redis(self.hostname, self.port)
        return self.__client

    def __getattr__(self, k):
        # forward non found attrs to self.redis_client
        return getattr(self.redis_client, k)