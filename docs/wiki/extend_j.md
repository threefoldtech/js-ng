# Extending Jumpscale
In order to extend jumpscale or `j` object you need to add your code in one of the namespaces we have `data`, `sals`, `clients`, `tools`, `servers` as a package.

## Deciding on how to expose your extension

### using package init file
If simple extension you can just write your code in `yourpackage/__init__.py` file, the same way we do in lots of `data` helpers and in `j.sals.fs`

### Replace loaded package

The way we do for faker data package we replace the package completely with one instance of `Faker`.
```
def export_module_as():
    from faker import Faker
    import sys

    return Faker()
```

### Import all from another package
Same way we do in `data.time` package

```
from arrow import *
```

### Replace the loaded package with a specific factory
The same way we do for the clients by replacing the loaded client package with one instance of a factory of the client

```python

def export_module_as():
    from jumpscale.core.base import StoredFactory
    from .redis import RedisClient


    return StoredFactory(RedisClient)

```

## export_module_as

`export_module_as` is our mechanism to define how to expose a certain package under j object. In case it's defined in the package we replace the package with its value.

