# Developing clients

Client is also almost like a [SAL](./developing_sal.md), but requires configuration management at some point and maybe credentials, and can have multiple objects. e.g redis client for my localhost and one to another remote redis machine

## Code structure

One of the simplest clients we have is `redis` client

```
jumpscale/clients/redis
├── __init__.py
└── redis.py
```
You create your client as a package (`__init__.py` file and any other files you need)

## Writing code

A Typical client should inherit from `j.clients.base.Client`

```python
class RedisClient(Client):
    hostname = fields.String(default="localhost")
    port = fields.Integer(default=6379)
    password = fields.Secret()
```
And then we define the fields relevant to the client as class attributes using our `jumpscale.core.base.fields`. Make sure to review the [baseclasses](../baseclasses.md) and [config management](../configmgmt.md) sections


Here's the full code of redis client as of the moment.
```python
"""
Redis client
"""

from redis import Redis

from jumpscale.clients.base import Client
from jumpscale.core.base import fields
from jumpscale.core.base.events import AttributeUpdateEvent


class RedisClient(Client):
    hostname = fields.String(default="localhost")
    port = fields.Integer(default=6379)
    password = fields.Secret()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

    def __getattr__(self, k):
        # forward non found attrs to self.redis_client
        return getattr(self.redis_client, k)
```
### Exposing the client as factory

```
from jumpscale.core.base import StoredFactory
from .redis import RedisClient

export_module_as = StoredFactory(RedisClient)
```
We use `export_module_as` feature to bind `j.clients.redis` to factory of RedisClient
