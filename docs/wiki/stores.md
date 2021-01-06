# Store backend and search

Content:

* [Introduction](#introduction)
    * [Current Backends](#current-backends)
        * [Filesystem](#filesystem)
        * [Redis](#redis)
        * [Whoosh](#whoosh)
    * [Factory options](#factory-options)
        * [Always reload](#always-reload)
* [Locations](#locations)
* [Search](#search)
    * [Whoosh search](#whoosh-search)
* [Writing a store backend](#writing-a-store-backend)
    * [Interface](#interface)
    * [Serialization](#serialization)
    * [Location and type information](#location-and-type-information)
    * [A complete implementation](#a-complete-implementation)


## Introduction

A store backend is used to store configuration data, regardless of its format or content. the backend is selected automatically from the configuration file (`config.toml`).

In all cases, we don't deal with stores directly, but through factories.

### Current backends

We now support multiple storage backend, every backend stores the data differently, and they don't share the data between them.

Selecting any of them can be done using the configuration file, or using `jsctl`:

```bash
jsctl config update store redis
```

Each store have related configuration:

```bash
cat ~/.config/jumpscale/config.toml

...

[stores]

[stores.redis]
hostname = "localhost"
port = 6379

[stores.filesystem]
path = "/home/abom/.config/jumpscale/secureconfig"

[stores.whoosh]
path = "/home/abom/.config/jumpscale/whoosh_indexes"
```

For example, you can specify which redis server you need to use.

#### Filesystem

Stores configuration as a directory tree. does not support indexing/search. The path where data is stored can be configured.

#### Redis
Stores configuration as relative key/values. does not support indexing/search, Server information can be configured.

#### Whoosh

Stores configuration in whoosh indexes. it supports indexing/search for the following field types:

* Boolean
* Bytes
* Email (as strings)
* GUID (as strings)
* IPAddress (as strings)
* IPRange (as strings)
* Json (as strings)
* Path (as strings)
* String
* Tel (as strings)
* URL (as strings)
* Integer
* Port
* Date (as integers)
* DateTime (as integers)
* Time (as integers)

Some known issues:

* Field names follow `whoosh` constraints, e.g. cannot start with underscore.
* For `Float` fields, it has known issue, can be resolved by using integers (with compute function) or even a string for now.

The path where whoosh indexes are created can be configured.

### Factory options

Factory options can be set in config file, only always reload option is available for now.

### Always reload

When you load an object from a factory, it will stay in memory for fast access, but sometimes, you need to always fetch the new data (this might be heavy but useful in e.g multi-process setup).

In jumpscale configuration, you can set `always_load` in factory setting section:

```
[factory]
always_reload = false
```

If set to true, the following example would work (from two different shells):

First get an instance in the first shell:

```python
JS-NG> cl = j.clients.redis.get("aa")
JS-NG> cl.hostname
'localhost'
```

Also, get the same instance in the second shell:

```python
JS-NG> cl = j.clients.redis.get("aa")
JS-NG> cl.hostname
'localhost'
```

Update `hostname` in the first shell:

```python
JS-NG> cl.hostname = "172.17.0.2"
JS-NG> cl.save()
```

If you try to get the same instance in the second shell again, it should get the latest stored data:

```python
JS-NG> cl = j.clients.redis.get("aa")
JS-NG> cl.hostname
'172.17.0.2'
```

## Locations

To distinguish between every base class/type and different instances, we have a dynamic location generated for every factory, for example, if you tried the following code in `jsng` shell:


```python
JS-NG> from jumpscale.core.base import Base, fields, StoredFactory
     2
     3 class Car(Base):
     4     color = fields.String()
     5
     6
     7 factory = StoredFactory(Car)
JS-NG> factory.location
Location('jumpscale.entry_points.jsng', 'Car')
```

Cars factory now have an auto-generated location from module and class/type name.

Different store backends benefit from this, as it can get the unique key for each instance configuration that need to be stored by just appending this location to the instance name.


## Search

By default, if the backend does not support search, it will have a generic linear search function, which iterates over all stored configuration and do the search.

Generic search is done using factory `find_many`, it can accept `cursor_`, `limit_` and query mapping as field/value:

`cursor_` is an optional field name to start searching from (assuming they've the same order every time).

`limit_` is the number of results to return.

`find_many` will return a tuple, containing a new cursor (if available), the count of results and a generator containing the objects.


```python

JS-NG> j.clients.redis.list_all()
{'bb', 'aa', 'main'}

JS-NG> new_cursor, count, res = j.clients.redis.find_many(limit_=1, port=6379)
JS-NG> new_cursor
'bb'

JS-NG> count
1

JS-NG> list(res)
[RedisClient(_Base__instance_name='port', _Base__parent=None, _RedisClient__client=None, __hostname='localhost', __password='', __port=6379, _factories={}, save=functools.partial(<bound method StoredFactory._validate_and_save_instance of <jumpscale.core.base.factory.jumpscaleclientsredisredisRedisClient object at 0x7f211a907d30>>, RedisClient(...)))]
```


To fetch the next patch, just call `find_many` again with the new cursor:

```python
JS-NG> new_cursor, count, res = j.clients.redis.find_many(limit_=1, cursor_=new_cursor, port=6379)
JS-NG> new_cursor
'aa'

JS-NG> count
1

JS-NG> list(res)
[RedisClient(_Base__instance_name='port', _Base__parent=None, _RedisClient__client=None, __hostname='localhost', __password='', __port=6379, _factories={}, save=functools.partial(<bound method StoredFactory._validate_and_save_instance of <jumpscale.core.base.factory.jumpscaleclientsredisredisRedisClient object at 0x7f211a907d30>>, RedisClient(...)))]
```

### Whoosh search

If you wanted indexing, with [complex query support](https://whoosh.readthedocs.io/en/latest/querylang.html), whoosh backend would be the right solution.

It follows the same interface as the generic search, but the cursor is passed as pages, as `whoosh` support pagination this way.


```python
S-NG> j.clients.redis.list_all()
{'aa', 'bb', 'dd'}

JS-NG> new_cursor, count, res = j.clients.redis.find_many(limit_=1, port=6379)
JS-NG> new_cursor
2

JS-NG> count
1

JS-NG> list(res)
[RedisClient(_Base__instance_name='bb', _Base__parent=None, _RedisClient__client=None, __hostname='localhost', __password='B0TLe/zbRFBPoyJF6xYz4al0Vl
tauWnXUhiw5bK6XwYi1i+rpbFY1Q==', __port=6379, _factories={}, save=functools.partial(<bound method StoredFactory._validate_and_save_instance of <jumps
cale.core.base.factory.jumpscaleclientsredisredisRedisClient object at 0x7faab40f4438>>, RedisClient(...)))]

JS-NG> new_cursor, count, res = j.clients.redis.find_many(limit_=1, cursor_=new_cursor, port=6379)
JS-NG> new_cursor
3

JS-NG> count
1

JS-NG> list(res)
[RedisClient(_Base__instance_name='aa', _Base__parent=None, _RedisClient__client=None, __hostname='hamadaaaa', __password='CMUianZyQcrOOL4ue7EvZrwZ4$ck23L95lVg2SPlAjg2rti1k767kw==', __port=6379, _factories={}, save=functools.partial(<bound method StoredFactory._validate_and_save_instance of <jump$cale.core.base.factory.jumpscaleclientsredisredisRedisClient object at 0x7faab40f4438>>, RedisClient(...)))]

```


Field queries can contain normal `whoosh` operators and will be combined by `OR`:

```python
S-NG> new_cursor, count, res = j.clients.redis.find_many(hostname="local*", port=6379)
JS-NG> count
2

JS-NG> list(res)
[RedisClient(_Base__instance_name='bb', _Base__parent=None, _RedisClient__client=None, __hostname='localhost', __password='B0TLe/zbRFBPoyJF6xYz4al0VltauWnXUhiw5bK6XwYi1i+rpbFY1Q==', __port=6379, _factories={}, save=functools.partial(<bound method StoredFactory._validate_and_save_instance of <jumpscale.core.base.factory.jumpscaleclientsredisredisRedisClient object at 0x7faab40f4438>>, RedisClient(...))), RedisClient(_Base__instance_name='dd', _Base__parent=None, _RedisClient__client=None, __hostname='localhost', __password='NLFSdK/qC8qwlPOONU1Av1Xsmk7bAWyPv0YYyN2fG7cwmPGioqyX/Q==', __port=6379, _factories={}, save=functools.partial(<bound method StoredFactory._validate_and_save_instance of <jumpscale.core.base.factory.jumpscaleclientsredisredisRedisClient object at 0x7faab40f4438>>, RedisClient(...)))]
```


## Writing a store backend

To write a store backend, you need to implement the store interface and inherit from `EncryptedConfigStore` where all of encryption related stuff is implemented, and you don't need to do any additional operations.


For example, the following memory store can be like:

```python

from . import ConfigNotFound, EncryptedConfigStore
from .serializers import JsonSerializer

class MemoryStore(EncryptedConfigStore):
    """
    Stores config in memory
    """

    def __init__(self, location):
        """
        memory store with config stored in a map (dict)

        Args:
            location (Location): where config will be stored per instance
        """
        super(MemoryStore, self).__init__(location, JsonSerializer())
        self.configs = {}

...
```

### Interface

You need to implement the following methods for your store, except `find` as it's not mandatory (already implemented by `EncryptedConfigStore`).

```python
class ConfigStore(ABC):
    """
    the interface every config store should implement:

    - `read(instance_name)`:  reads the data of this instance name
    - `write(instance_name, data)`: writes the data of this instance
    - `list_all(instance_name)`: lists all instance names
    - `delete(instance_name)`: delete instance data
    - `find(self, cursor_=None, limit_=None, **query)`: optional search method with query as field mapping
    """

    @abstractmethod
    def read(self, instance_name):
        pass

    @abstractmethod
    def write(self, instance_name, data):
        pass

    @abstractmethod
    def list_all(self):
        pass

    @abstractmethod
    def find(self, cursor_=None, limit_=None, **query):
        pass

    @abstractmethod
    def delete(self, instance_name):
        pass
```

### Serialization

The serializer passed in `__init__` will be used with when passing/getting the data from your implementation, so for example, if you used a `JsonSerializer`, you expect `write` method to accept `data` as a `JSON` string, and you should return it in `read` also as a `JSON` string.


```python
    ...

    def __init__(self, location):
        """
        memory store with config stored in a map (dict)

        Args:
            location (Location): where config will be stored per instance
        """
        super(MemoryStore, self).__init__(location, JsonSerializer())
        self.configs = {}
```

If you want the data to be untouched and work with it as a dict directly, use `Serializer` instead.

```python
    from . import Serializer
    ...

    def __init__(self, location):
        """
        memory store with config stored in a map (dict)

        Args:
            location (Location): where config will be stored per instance
        """
        super(MemoryStore, self).__init__(location, JsonSerializer())
        self.configs = {}
```

The data will be a dict that can be serialized in any format (as it will only contain primitive data types, converted using `Base`).

### Location and type information

To help organize the data for the factory, the store will be given a location, this location can be like `Location('jumpscale.entry_points.jsng', 'Car')`.

So, it can be useful to generate unique keys, paths..etc for every instance data.

Full location name (dot separated) can be accessed using `self.location.name`.

The type information is also stored in location objects, `self.location.type` would give you the current `Base` class/type, and you can get for examples current defined fields as `self.location.type._fields`


### A complete implementation

We will do the complete `MemoryStore`:


```python

from . import ConfigNotFound, EncryptedConfigStore
from .serializers import JsonSerializer

class MemoryStore(EncryptedConfigStore):
    """
    Stores config in memory
    """

    def __init__(self, location):
        """
        memory store with config stored in a map (dict)

        Args:
            location (Location): where config will be stored per instance
        """
        super(MemoryStore, self).__init__(location, JsonSerializer())
        self.configs = {}

    def get_instance_key(self, instance_name):
        return f"{self.location.name}.{instance_name}"

    def write(self, instance_name, data):
        key = self.get_instance_key(instance_name)
        self.configs[key] = data

    def read(self, instance_name):
        key = self.get_instance_key(instance_name)
        try:
            return self.configs[key]
        except KeyError:
            raise ConfigNotFound(f"cannot find config for {instance_name}")

    def delete(self, instance_name):
        key = self.get_instance_key(instance_name)
        if key in self.configs:
            del self.configs[key]

    def list_all(self):
        return self.configs.keys()
```


As you can see, we used the location to get a unique key for each instance.

For more advanced implementations, have a look at `jumpscale.core.store` module.
