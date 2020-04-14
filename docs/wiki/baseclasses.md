# Base classes

We have some base classes for mainly creating factories with instances of certain type and it also provides configuration management for this instances (securly saved).


## Base

Base is the type where any configuration can be defined:

```python
from jumpscale.core.base import Base, fields


class Address(Base):
    x = fields.Integer()
    name = fields.String()

    def __init__(self):
        super().__init__()
        self.x = 123


class Wallet(Base):
    ID = fields.Integer()
    addresses = fields.Factory(Address)


class User(Base):
    wallets = fields.Factory(Wallet)


user = User()
w = user.wallets.get("aa")

addr1 = w.addresses.new("mine")
addr1.x = 456
addr2 = w.addresses.new("another")
addr2.x = 680
w.addresses.delete("another")
```

Note that, these configuration is not yet stored or saved, you need to use a [stored factory](stored-factory) with this `Base` type.

## Stored factory

The backend to store configurations of `Base` types where can create, list and delete instances.

- Support encryption via secret fields (`fields.Secret`)
- Multiple storage backends (FileSystemStore, RedisStore)

Example:

```python
class Address(Base):
    x = fields.Integer()
    name = fields.String()

    def __init__(self):
        super().__init__()
        self.x = 123


class Wallet(Base):
    ID = fields.Integer()
    addresses = fields.Factory(Address)


class User(Base):
    name = fields.String()
    wallets = fields.Factory(Wallet)


users = StoredFactory(User)
user1 = users.get("user1")
print(user1.instance_name)
user1.name = "ahmed"
user1.save()
```

## Fields

Fields of the config
can have default value, required or optional, indexed or not, set of validators as well

See a complete list of available fields at https://js-next.github.io/js-ng/api/jumpscale/core/base/fields.html.


## Clients

Clients can be defined the same as any Base class, they're a special type of `Base`


```python
"""
Redis client
"""

from redis import Redis

from jumpscale.core import events

from jumpscale.clients.base import Client
from jumpscale.core.base import fields
from jumpscale.core.base.events import AttributeUpdateEvent


class RedisClientAttributeUpdated(AttributeUpdateEvent):
    pass


class RedisClient(Client):
    hostname = fields.String(default="localhost")
    port = fields.Integer(default=6379)

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
        return list(self.__dict__.keys()) + dir(self.redis_client)

    @property
    def redis_client(self):
        if not self.__client:
            self.__client = Redis(self.hostname, self.port)
        return self.__client

    def __getattr__(self, k):
        # forward non found attrs to self.redis_client
        return getattr(self.redis_client, k)

```

Then we can simply create a stored factory for this client as:

```python
redis = StoredFactory(RedisClient)
```



## Data updates

In your instance, you can implement `_attr_updated` to handle attribute updates, but by default, an event of the type `AttributeUpdateEvent` is fired.

Using events here allow other components to handle events related to your base implementation too.

An example of using `attr_updated` or events to re-create an inner client (redis):

Using `_attr_updated`:

```python
class RedisClient(Client):
    hostname = fields.String(default="localhost")
    port = fields.Integer(default=6379)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = Redis(self.hostname, self.port)

    def _attr_updated(self, name, value):
        # reset to get a new client
        if name == 'hostname':
            self.client = Redis(value, self.port)
        elif name == 'port':
            self.client = Redis(self.hostname, value)

```

Or using events (so, others can know of this change too):

```python
class RedisClientAttributeUpdated(AttributeUpdateEvent):
    pass


class RedisClient(Client):
    hostname = fields.String(default="localhost")
    port = fields.Integer(default=6379)

    def __init__(self):
        self.__client = None
        super().__init__()

    @property
    def client(self):
        if not self.__client:
            self.__client = Redis(self.hostname, self.port)
        return self.__client

    def _attr_updated(self, name, value):
        # calling super()._attr_updated is optional, as it will also notify
        # with an event type of AttributeUpdateEvent
        # super()._attr_updated(name, value)
        # this will allow other people to listen to this event too
        event = RedisClientAttributeUpdated(self, name, value)
        events.notify(event)

        # reset client
        self.__client = None


class ImplThatDependsOnRedisClientChange(events.Handler, Base):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs):
        # listen to this event
        events.add_listenter(self, RedisClientAttributeUpdated)

    def handle(self, ev):
        # do something with ev.instance...etc
```

We created our own custom event type of `RedisClientAttributeUpdated`.

In case of any changes, we notify others that the client attribute changed, and also, handle this change too, by using `events.add_listenter(self, RedisClientAttributeUpdated)`.
