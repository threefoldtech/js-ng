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

## Data and sub-factory updates

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
