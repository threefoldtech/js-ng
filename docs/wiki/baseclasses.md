# Base classes

We have some base classes for mainly creating factories with instances of certain type and it also provides configuration management for this instances (securly saved).


## Base
## StoredFactory

The backend to store configurations
- can be encrypted or plain
- Multiple backends (FileSystemStore, RedisStore)


## Fields

Fields of the config
can have default value, required or optional, indexed or not, set of validators as well

Available fields:
- boolean
- integer
- Float
- string
- Secret (for storing passwords)
- Object
- List (for collections)

## Data updates

In your instance, you can implement `_attr_updated` to handle attribute updates, but by default, an event of the type `AttributeUpdateEvent` is fired with the instance and the name alongside the new value.

Using events here allow other components to handle events related to your base implementation too.


An example of using `attr_updated` or events to re-create an inner client (redis):

Using `_attr_updated`:

```python


class RedisClient(Client):
    hostname = fields.String(default="localhost")
    port = fields.Integer(default=6379)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__client = None

    @property
    def client(self):
        if not self.__client:
            self.__client = Redis(self.hostname, self.port)
        return self.__client

    def _attr_updated(self, name, value):
        # reset to get a new client
        self.client__ = None
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

### Example

```python
import unittest


# TODO: move fields to fields or types module
from jumpscale.core.base import Base, Factory, StoredFactory, DuplicateError, fields


class Address(Base):
    x = fields.Integer()
    name = fields.String()

    def __init__(self):
        super().__init__()
        self.x = 123


class Wallet(Base):
    ID = fields.Integer()
    addresses = fields.Factory(Address)


class Client(Base):
    wallets = fields.Factory(Wallet)


class TestStoredFactory(unittest.TestCase):
    def setUp(self):
        self.factory = StoredFactory(Client)

    def test_create_stored_factory(self):
        cl = self.factory.new("client")
        w = cl.wallets.get("aa")
        self.assertEqual(cl.wallets.count, 1)

        addr1 = w.addresses.new("mine")
        addr1.x = 456
        addr2 = w.addresses.new("another")
        addr2.x = 680
        self.assertEqual(w.addresses.count, 2)
        w.addresses.delete("another")
        self.assertEqual(w.addresses.count, 1)

        # test duplicates
        with self.assertRaises(DuplicateError):
            w.addresses.new("mine")

        # create another instance
        new_cl = Client()
        self.assertEqual(new_cl.wallets.count, 0)

    def tearDown(self):
        for name in self.factory.store.list_all():
            self.factory.delete(name)

```


## Clients

Example for defining a client

```

class GedisClient(Client):
    name = fields.String(default="local")
    hostname = fields.String(default="localhost")
    port = fields.Integer(default=16000)

```
