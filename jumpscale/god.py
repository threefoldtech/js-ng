import os
import importlib
import pkgutil
import importlib.util

# import lazy_import

"""
the idea is with hierarchy like this

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

- we get all the paths of the `rootnamespace`
- we get all the subnamespaces
- we get all the inner packages and import all of them (lazily) or load them eagerly but just once.


real example:
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
│   ├── god.py
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
js-ext
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


"""

__all__ = ["j"]


def load():
    import jumpscale

    loadedspaces = []
    for jsnamespace in jumpscale.__path__:
        for root, dirs, files in os.walk(jsnamespace):
            for d in dirs:
                if d == "__pycache__":
                    continue
                if os.path.basename(root) == "jumpscale":
                    continue
                # print("root: {} d: {}".format(root, d))
                rootbase = os.path.basename(root)
                loadedspaces.append(rootbase)
                pkgname = d
                importedpkgstr = "jumpscale.{}.{}".format(rootbase, pkgname)
                __all__.append(importedpkgstr)
                # print("import: ", importedpkgstr)
                # globals()[importedpkgstr] = lazy_import.lazy_module(importedpkgstr)
                globals()[importedpkgstr] = importlib.import_module(importedpkgstr)

    return loadedspaces


class J:
    """
        Here we simulate god object `j` by delegating the calls to suitable subnamespace

    """

    def __init__(self):
        self._loadednames = set()
        self._loadedallsubpackages = False
        self.__loaded = []

    def __dir__(self):
        return self.__loaded

    @property
    def logger(self):
        import jumpscale.core.logging
        return jumpscale.core.logging.logger
    
    @property
    def config(self):
        import jumpscale.core.config
        return jumpscale.core.config

    @property
    def exceptions(self):
        import jumpscale.core.exceptions
        return jumpscale.core.exceptions
    
    def __getattr__(self, name):
        import jumpscale

        if not self._loadedallsubpackages:
            self.__loaded = load()
            self._loadedallsubpackages = True

        if name not in self._loadednames:
            # print("name : ", name)
            self._loadednames.add(name)
            # load()
            importlib.import_module("jumpscale.{}".format(name))
            for m in [x for x in globals() if "jumpscale." in x]:
                parts = m.split(".")[1:]
                obj = jumpscale
                while parts:
                    p = parts.pop(0)
                    obj = getattr(obj, p)
                    # print(obj)
                try:
                    for attr in dir(obj):
                        try:
                            # print("getting attr {} from obj {}".format(attr, obj))
                            getattr(obj, attr)
                        except Exception:
                            pass
                except:
                    print("can't dir object: ", obj)

        return getattr(jumpscale, name)


j = J()
