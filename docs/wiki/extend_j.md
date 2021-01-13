# Extending Jumpscale
In order to extend jumpscale or `j` object you need to add your code in one of the namespaces we have `data`, `sals`, `clients`, `tools`, `servers` as a package.

Contents:

- [Extending Jumpscale](#extending-jumpscale)
  - [export_module_as](#export_module_as)
  - [Deciding on how to expose your extension](#deciding-on-how-to-expose-your-extension)
    - [Using package init file](#using-package-init-file)
    - [Replace loaded package](#replace-loaded-package)
    - [Import all from another package](#import-all-from-another-package)
    - [Replace the loaded package with a specific factory](#replace-the-loaded-package-with-a-specific-factory)
  - [Optional modules](#optional-modules)


## export_module_as

`export_module_as` is our mechanism to define how to expose a certain package under j object. In case it's defined in the package we replace the package with its value.


## Deciding on how to expose your extension

### Using package init file
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

## Optional modules

If your module depend on [optional (extra) dependency](https://python-poetry.org/docs/pyproject/#extras), you can mark it with `__optional__ = True` before you do your imports in `export_module_as`. This will allow the loader to show a useful message to users if the optional dependency was not installed in the first place.

For example, module `j.data.fake` depends on `faker` package, the module is exported as:

```
__optional__ = True

def export_module_as():
    from faker import Faker
    ...
    ...
```

So, if `faker` package was not installed by default, it will raise an exception with a message that instructs the user how to install this dependency.

```
JS-NG> j.data.fake
...
...
jumpscale.loader.OptionalModuleError: module was not installed, try installing again with 'fake' as an extra
e.g. 'poetry install -E fake' or 'pip install js-ng[fake]'
```
