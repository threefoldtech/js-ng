# J Object
A global j object for easy access to components and functionalities (e.g. god object anti-pattern).

* Should allow auto-completions (without the need to evaluate!)
* Easy to register objects/components.

## Use modules

Utilize code structure to get the idea of a global j object, by simply arranging modules like:

```
jumpscale
  mod
    submod
      impl.py
```


impl.py

```

class CoreImpl:
  ....


core = CoreImpl()
```


Accessing from other places

```
import jumpscale as j

j.mod.submod.impl.core
```

Other principles like state management need to be discussed (also make sure it would cover actual jumpscale usescaes).



# Problem 1: Code Structure


We can use [namespaces](https://www.python.org/dev/peps/pep-0382/) the way `zope` does with [zope.interface](https://pypi.org/project/zope.interface/) for example.
Now we can easily have `jumpscale.sal` , `jumpscale.clients` easily separated into there own pip packages like any normal python project. (bye bye installtools!)

## declaring namespaces
One of two ways

1- remove `__init__.py`
2- add namespace declaration in `__init__.py` `__import__('pkg_resources').declare_namespace(__name__)`

Example structure

```text
.
├── projectclients
│   └── jumpscale
│       ├── clients
│       │   ├── github.py
│       │   ├── gogs.py
│       │   ├── __init__.py
│       ├── __init__.py

├── projectmain
│   └── jumpscale
│       ├── god.py
│       ├── __init__.py
├── projectsals
│   └── jumpscale
│       ├── __init__.py
│       └── sal
│           ├── fs.py
│           ├── __init__.py
└── projecttools
    └── jumpscale
        ├── __init__.py
        └── tools
            ├── __init__.py
            └── sync.py
```

# Problem 2: implicit imports (autoloading subpackages)

jumpscale by design wants the least amount of imports thats why all are registered under j

e.g for `sal/__init__.py`
```
import pkgutil

__all__ = []
for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    __all__.append(module_name)
    _module = loader.find_module(module_name).load_module(module_name)
    globals()[module_name] = _module
```
CHECK: lazyloader/import hooks  in stdpython
 https://docs.python.org/3/library/importlib.html#importlib.util.LazyLoader
# Problem 3: Singletons
Solved by design using python modules


# Problem 4: jslocation

If we open `god.py`

```python
import jumpscale.sal
import jumpscale.tools
import jumpscale.clients

j = jumpscale
```
we have handcrafted imports for sal, tools, clients so their subpackages can be autoloaded, but how should it work with packages like `digitalme`

## How to register digitalme in the god object
Do we generate `import jumpscale.digitalme`? is there a standard python way to do it? a reliable plugin system?

## where would its module be registered?
for instance there might be `digitalme.tools` should it be under `j.tools` directly or `j.digitalme.tools`? I prefer the latter for clarity and conflict resolution too

# Example usage with jumpscale

```
~> export PYTHONPATH="projecttools:projectsals:projectclients:projectmain"
```

```ipython
In [1]: import jumpscale.loader

In [2]: jumpscale.sal.fs.copyfile('a', 'b')
copying file

In [3]: jumpscale.tools.sync.sync()
sync tool

In [4]: jumpscale.clients.github.get_githubclient?
Signature: jumpscale.clients.github.get_githubclient(username, password)
Docstring: <no docstring>
File:      ~/wspace/jumpscale-skeleton/projectclients/jumpscale/clients/github.py
Type:      function

In [5]: jumpscale.clients.github.get_githubclient('a', 'bb')
getting client with a bb

In [6]: jumpscale.clients.gogs.get_gogs('a', 'bbb') # uses jumpscale sal.fs in its code
sync tool
getting gogs client with a bbb
```


# Example usage with `j`

```python

In [1]: from jumpscale.loader import j

In [2]: j.sal.fs.removefile('a')
removing file

In [3]: j.clients.gogs.get_gogs('a', 'b')
sync tool
getting gogs client with a b

```
