# Configuration Management

We provide a mechanism for storing and retrieving configurations of different clients, servers and services securely, any type of a resource or a client that needs configuration, it can simply implemented using base classes.

- [Introduction](#Introduction)
- [Storage](#storage)
- [Encryption](#encryption)
- [More on base classes](#more-on-base-classes)


## Introduction

To define any type of resource, you can create a class, with different configuration fields, and a factory, which will manage this class instances.

Consider having remote machines, where every machine have an ip address and a region:

```python
from enum import Enum

from jumpscale.core.base import Base, fields, StoredFactory
from jumpscale.clients.sshclient import sshclient

class Region(Enum):
    US = "us"
    EU = "eu"

class Machine(Base):
    ip = fields.IPAddress()
    region = fields.Enum(Region)

machines = StoredFactory(Machine)
```

This simply define a resource called `Machine`, which have two fields.

`machines` here is factory, and it's the entry point where we can create and manage instances of this machines:

```python
m1 = machines.get("m1")
m1.ip = "127.0.0.1"
m1.region = "us"
m1.save()
```

`save` will store this configuration to current configured storage, and at any time, you can list current machines, delete any of them...etc:

```python
print(machines.list_all())
machines.delete("m1")
```

## Storage

Any stored factory has a store, which is selected based configuration.

For now, we have two types of storage:

* File system: by default, stores secure config under `~/.config/jumpscale/secureconfig`
* Redis: stores configuration at redis.


Implementation can be found at `jumpscale.core.base.store`, the main idea is that, every factory should store configuration on a unique location, this location is automatically generated, and instances are stored in a tree-like hierarchy.

For example:

```
➜  js-ng git:(development) ✗ tree ~/.config/jumpscale/secureconfig
/home/abom/.config/jumpscale/secureconfig
├── jumpscale
│   ├── clients
│   │   ├── docker
│   │   │   └── docker
│   │   │       └── DockerClient
│   │   │           └── test
│   │   │               └── data
│   │   ├── gdrive
│   │   │   └── gdrive
│   │   │       └── GdriveClient
│   │   │           └── test
│   │   │               └── data
│   │   ├── github
│   │   │   └── github
│   │   │       ├── Github
│   │   │       │   ├── g1
│   │   │       │   │   ├── data
│   │   │       │   │   └── users
│   │   │       │   │       └── jumpscale
│   │   │       │   │           └── clients
│   │   │       │   │               └── github
│   │   │       │   │                   └── github
│   │   │       │   │                       └── User
│   │   │       │   │                           └── u1
│   │   │       │   │                               └── data
```

### Serialization:

Only `json` serialization is now supported, if you need to get a serializable dict for any base class instance, just use `to_dict()` method.


## Encryption

We use public key encryption, implementation is at `j.data.nacl`.
For keys, we use the key that's generated and saved at `private_key_path`.
There is a key that's auto-generated for you, to generate a new key, use `hush_keygen` and `jsctl` to set the path:

```
hush_keygen --name test
jsctl config update --name=private_key_path --value="`pwd`/test.priv"
```

Only secret fields are encrypted by default, so, if you have a password field for example, it's better to use `fields.Secret` for it:

```python
class Region(enum):
    US = "us"
    EU = "eu"

class Machine(Base):
    ip = fields.IPAddress()
    region = fields.Enum(Region)
    username = fields.Secret()
    password = fields.Secret()
```

Now when the store writes any instance configuration of `Machine`, it will encrypt it.
If you load this instance again, it will be decrypted.

## More on base classes

You can check what base classes can provide, what are supported field types  and more at [Base classes](baseclasses.md).
