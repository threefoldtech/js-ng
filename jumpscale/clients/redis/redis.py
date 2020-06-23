"""
Redis client
"""

from redis import Redis, exceptions

from jumpscale.core import events

from jumpscale.clients.base import Client
from jumpscale.core.base import fields
from jumpscale.core.base.events import AttributeUpdateEvent


class RedisClientAttributeUpdated(AttributeUpdateEvent):
    pass


class RedisClient(Client):
    hostname = fields.String(default="localhost")
    port = fields.Integer(default=6379)
    password = fields.Secret(default="")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__client = None

    def _attr_updated(self, name, value):
        super()._attr_updated(name, value)
        # this will allow other people to listen to this event too
        event = RedisClientAttributeUpdated(self, name, value)
        events.notify(event)

        # reset client
        self.__client = None

    def __dir__(self):
        return list(self._fields.keys()) + dir(self.redis_client)

    @property
    def redis_client(self):
        if not self.__client:
            if self.password:
                self.__client = Redis(self.hostname, self.port, password=self.password)
            else:
                self.__client = Redis(self.hostname, self.port)

        return self.__client
    
    def is_running(self):
        try:
            return self.redis_client.ping()
        except exceptions.ConnectionError:
            return False

    def __getattr__(self, k):
        # forward non found attrs to self.redis_client
        return getattr(self.redis_client, k)
