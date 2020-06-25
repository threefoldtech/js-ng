# Loader implementation

For normal imports, we don't need a global `j` object, but for ease of access and the shell, we provide a loader which loads all sub-modules under `jumpscale` under a single object, and imports any module once it's accessed, see the following different examples:

Using direct **imports**:
```python
from jumpscale.sals import fs

print(fs.exists("/path/to/file"))
```

Using the **loader**:

```python
from jumpscale.loader import j

print(j.sals.fs.exists("/path/to/file"))
```

When using the loader, the module `jumpscale.sals.fs` won't be imported until accessed.


## Code structure
the idea is with hierarchy like this
```
project1/
         /rootnamespace (jumpscale)
            /subnamespace1
                ... pkg1
                ... pkg2
            /subnamespace2
                ... pkg1
                ... pkg2
project2/
         /rootnamespace (jumpscale)
            /subnamespace1
                ... pkg1
                ... pkg2
            /subnamespace2
                ... pkg1
                ... pkg2
```
- we get all the paths of the `root namespace`
- we get all the sub-namespaces
- we get all the inner packages and import any of them (lazily).


# real example
```
js-ng
├── jumpscale   <- root namespace
│   ├── clients  <- subnamespace where people can register on
│   │   ├── base.py
│   │   ├── github   <- package in subnamespace
│   │   │   ├── github.py
│   │   │   └── __init__.py
│   │   └── gogs
│   │       ├── gogs.py
│   │       └── __init__.py
│   ├── core
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   └── logging.py
│   ├── data
│   │   ├── idgenerator
│   │   │   ├── idgenerator.py
│   │   │   └── __init__.py
│   │   └── serializers
│   │       ├── __init__.py
│   │       └── serializers.py
│   ├── loader.py
│   ├── sals
│   │   └── fs
│   │       ├── fs.py
│   │       └── __init__.py
│   └── tools
│       └── keygen
│           ├── __init__.py
│           └── keygen.py
├── README.md
└── tests
    └── test_loads_j.py
```

```
js-sdk
├── jumpscale
│   ├── clients
│   │   └── gitlab
│   │       ├── gitlab.py
│   │       └── __init__.py
│   ├── sals
│   │   └── zos
│   │       ├── __init__.py
│   │       └── zos.py
│   └── tools
├── README.md
└── tests
    └── test_success.py
```


## How is it implemented?

The loader is implemented at `loader.py`.

Each namespace level is exposed as a container type/class with properties that map to its sub-modules.

All this classes are generated in runtime using `type` function.


The entry point is the `expose_all` function, which takes a root module object, and a container class, and exposes this module's sub-modules under this container.

```python
def expose_all(root_module: types.ModuleType, container_type: type):
    """
    exposes all sub-modules and namespaces to be available under given container type (class)

    Args:
        root_module (types.ModuleType): module
        ns_type (type): namepace type (class)
    """

    for path in root_module.__path__:
        for name in os.listdir(path):
            if not os.path.isdir(os.path.join(path, name)) or name == "__pycache__":
                continue

            lazy_import_property = get_lazy_import_property(name, root_module, container_type)
            setattr(container_type, name, lazy_import_property)
```


And it's used with a type called `J`:

```python
class J:
    @property
    def logger(self):
        return self.core.logging

    @property
    def application(self):
        return self.core.application

    @property
    def config(self):
        return self.core.config

    @property
    def exceptions(self):
        return self.core.exceptions


expose_all(jumpscale, J)
j = J()
```

## Lazy imports

Lazy imports are done via property access:

```
def get_lazy_import_property(name, root_module, container_type):
    def getter(self):
        inner_name = f"__{name}"
        if hasattr(self, inner_name):
            return getattr(self, inner_name)

        full_name = f"{root_module.__name__}.{name}"
        mod = importlib.import_module(full_name)
        if mod.__spec__.origin in ("namespace", None):
            # if this module is a namespace, create a new container type
            sub_container_type = get_container_type(full_name)
            # expose all sub-modules of this imported module under this new type too
            expose_all(mod, sub_container_type)
            new_module = sub_container_type()
        else:
            # if it's just a module
            if hasattr(mod, "export_module_as"):
                new_module = mod.export_module_as()
            else:
                new_module = mod

        setattr(self, inner_name, new_module)
        return new_module

    return property(getter)
```

So, when a property is accessed, it can be either:

* A namespace: we create a new container class for this namespace and use `expose_all` on it, and return an instance of this container class.
* A module: we just import this module and return it, also we check if it's `export_module_as` function, so we expose its return value instead if the module itself.
