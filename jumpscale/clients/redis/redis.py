from redis import Redis

from jumpscale.core import events

from jumpscale.clients.base import Client
from jumpscale.core.base import fields
from jumpscale.core.base.events import AttributeUpdateEvent


class ClientAttributeUpdated(AttributeUpdateEvent):
    pass


class RedisClient(events.Handler, Client):
    hostname = fields.String(default="localhost")
    port = fields.Integer(default=6379)

    def __init__(self):
        self.__client = None
        super().__init__()

        # listen to this event
        events.add_listenter(self, ClientAttributeUpdated)

    def _attr_updated(self, name, value):
        # this will allow other people to listen to this event too
        event = ClientAttributeUpdated(self, name, value)
        events.notify(event)

    def handle(self, ev):
        if ev.instance == self:
            self.__client = None

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
