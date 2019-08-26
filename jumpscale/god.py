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
    loadeddict = {'jumpscale':{}}
    for jsnamespace in jumpscale.__path__:
        for root, dirs, files in os.walk(jsnamespace):
            for d in dirs:
                if d == "__pycache__":
                    continue
                if os.path.basename(root) == "jumpscale":
                    continue

                
                if os.path.dirname(root) != jsnamespace:
                    continue
                # print("root: {} d: {}".format(root, d))
                rootbase = os.path.basename(root)
                loadeddict['jumpscale'].setdefault(rootbase, {})
                pkgname = d
                importedpkgstr = "jumpscale.{}.{}".format(rootbase, pkgname)
                __all__.append(importedpkgstr)
                # print("import: ", importedpkgstr)
                # globals()[importedpkgstr] = lazy_import.lazy_module(importedpkgstr)
                try:
                    m = importlib.import_module(importedpkgstr)
                except Exception as e:
                    print("[-] ", e)
                    continue
                else:
                    if rootbase == "clients":
                        # print("rootbase: ", rootbase, importedpkgstr)
                        # print(m.factory)
                        loadeddict['jumpscale'][rootbase][pkgname] = m.factory
                        # loadeddict[importedpkgstr] = m.factory
                    else:
                        loadeddict['jumpscale'][rootbase][pkgname] = m

    return loadeddict


class Group:
    def __init__(self, d):
        self.d = d
        for k,v in d.items():
            setattr(self, k, v)
    def __getattr__(self, a):
        return self.d[a]
    
    def __dir__(self):
        return list(self.d.keys())

class J:
    """
        Here we simulate god object `j` by delegating the calls to suitable subnamespace
    """
    def __init__(self):
        self.__loaded = False
        self.__loaded_dict = {}

    def __dir__(self):
        self._load()
        return list(self.__loaded_dict['jumpscale'].keys()) + ['config', 'exceptions', 'logger']

    @property
    def logger(self):
        return self.__loaded_dict['jumpscale']['core']['logging'].logger
    
    @property
    def config(self):
        return self.__loaded_dict['jumpscale']['core']['config']

    @property
    def exceptions(self):
        return self.__loaded_dict['jumpscale']['core']['exceptions']
    
    def reload(self):
        self.__loaded = False
        self.__loaded_dict = {}

    def _load(self):
        if not self.__loaded:
            self.__loaded_dict = load()

    def __getattr__(self, name):
        self._load()
        
        d = self.__loaded_dict['jumpscale'][name]
        return Group(d)
       
j = J()

# jcode = """
# class J_codegen:

#     def __init__(self):
#         self.__loaded = False
#         self.__loaded_dict = {}

#     # def __dir__(self):
#     #     self._load()
#     #     return list(self.__loaded_dict['jumpscale'].keys()) + ['config', 'exceptions', 'logger']

#     @property
#     def logger(self):
#         return self.__loaded_dict['jumpscale']['core']['logging'].logger
    
#     @property
#     def config(self):
#         return self.__loaded_dict['jumpscale']['core']['config']

#     @property
#     def exceptions(self):
#         return self.__loaded_dict['jumpscale']['core']['exceptions']
    
#     def reload(self):
#         self.__loaded = False
#         self.__loaded_dict = {}

#     def _load(self):
#         if not self.__loaded:
#             self.__loaded_dict = load()

#     {% for group, _ in groups.items() %}
#     @property
#     def {{group}}(self):
#         self._load()

#         return Group(self.__loaded_dict['jumpscale']['{{group}}'])

#     {% endfor %}

# """

# def get_j_class():
#    import jinja2
#     jtemplate = jinja2.Template(jcode)
#     return jtemplate.render(groups=load()['jumpscale'])

# jclass = get_j_class()
# print(jclass)
# exec(jclass)
# j = J_codegen()

