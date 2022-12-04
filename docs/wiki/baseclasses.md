# Base classes

We have some base classes for mainly creating factories with instances of certain types.


## Base

Base is the type where any configuration can be defined:

```python
from jumpscale.core.base import Base, fields


class Address(Base):
    x = fields.Integer()
    name = fields.String()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

### Overriding constructor for Base sub-classes

When you override the consturctor of `Base` sub-classes, you need to pass all arguments to super `Base`, you can simply use `super().__init__(*args, **kwargs)`, like:

```python
class Address(Base):
    x = fields.Integer()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.x = 123
```


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

See a complete list of available fields at https://threefoldtech.github.io/js-ng/api/jumpscale/core/base/fields.html.


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



## Data updates and computed fields

In your instance, you can handle data updates in many ways, from triggering a handler on single field updates, to event-based system.

The following are three different ways to do it:

- [Base classes](#base-classes)
  - [Base](#base)
    - [Overriding constructor for Base sub-classes](#overriding-constructor-for-base-sub-classes)
  - [Stored factory](#stored-factory)
  - [Fields](#fields)
  - [Clients](#clients)
  - [Data updates and computed fields](#data-updates-and-computed-fields)
    - [Single field updates](#single-field-updates)
    - [Computed and non-stored fields](#computed-and-non-stored-fields)
    - [Attribute updates and events](#attribute-updates-and-events)

### Single field updates

If you need to do an action only when a single field is changed, You can use `on_update` for any field, which should be a callable that takes the instance and new value, see stellar client as an example:

```python
class Stellar(Client):
    network = fields.Enum(Network)
    address = fields.String()

    def secret_updated(self, value):
        self.address = stellar_sdk.Keypair.from_secret(value).public_key

    secret = fields.String(on_update=secret_updated)
```

In this code, we set a new value for the address in case the secret is updated.

### Computed and non-stored fields

Sometimes you need a field to be computed from other multiple fields, in such case, you just need to provide a `compute` function which takes current instance and it should return the computed value, see the following example:

```python
class User(Base):
    emails = fields.List(fields.String())
    first_name = fields.String(default="")
    last_name = fields.String(default="")

    def get_full_name(self):
        name = self.first_name
        if self.last_name:
            name += " " + self.last_name
        return name

    def get_unique_name(self):
        return self.full_name.replace(" ", "") + ".user"

    full_name = fields.String(compute=get_full_name)
    unique_name = fields.String(compute=get_unique_name)


users = StoredFactory(User)
user1 = users.get("test1")

print(user1.full_name)  #=> "ahmed mohamed"
print(user1.unique_name)  #=> "ahmedmohaed.user"

user1.first_name = "x"
user1.last_name = "y"
user1.save()
```

Note that, when saving the user object with this factory, the computed field will be saved too.

In other cases, you need to create a non-stored computed fields, which also do not need any serialization, but only to be created and used at run-time, this can be done by passing `stored=False` to this field (which is `True` by default):

```python
class Greeter:
    def __init__(self, name):
        self.name = name

    def say(self):
        print("hello", self.name)


class User(Base):
    first_name = fields.String(default="")
    last_name = fields.String(default="")

    def get_full_name(self):
        name = self.first_name
        if self.last_name:
            name += " " + self.last_name
        return name

    full_name = fields.String(compute=get_full_name)

    def get_my_greeter(self):
            return Greeter(self.full_name)

    my_greeter = fields.Typed(Greeter, stored=False, compute=get_my_greeter)
    ahmed_greeter = fields.Typed(Greeter, stored=False, default=Greeter("ahmed"))



users = StoredFactory(User)
user = users.get("test1")

user.first_name = "abdo"
user.last_name = "tester"
user.my_greeter.say()  #=> "hello abdo tester"
user.ahmed_greeter.say()  => "hello ahmed"
user.save()
```

we created two `Typed` fields of `Greeter` class, and used them without any problems, when saving this instance, these fields won't be serialized nor stored.

### Attribute updates and events

A more advanced feature are events and `_attr_updated` method, in any instance, you can override `_attr_updated` to handle attribute updates, also by default, an event of the type `AttributeUpdateEvent` is fired.

Using events can allow other components to handle events related to your base implementation, so it's not needed unless you need other people to know about your changes.

In this way, the instance receives a call or an `AttributeUpdateEvent` for any attribute.

An example of using `attr_updated` or events to re-create an inner client (redis), as the client need to re-created if any of `hostname` or `port` has been changed:

__Using__ `_attr_updated`:

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

__Or using__ events (so, others can know of this change too):

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
