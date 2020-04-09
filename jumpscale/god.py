"""This module coverts the god object j and its loading process.
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
- we get all the paths of the `rootnamespace`
- we get all the subnamespaces
- we get all the inner packages and import all of them (lazily) or load them eagerly but just once.


real example:
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
```
"""


import sys
import os
import traceback
import importlib
import pkgutil
import importlib.util
import docker

__all__ = ["j"]


def load():
    import jumpscale

    loadeddict = {"jumpscale": {}}
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
                loadeddict["jumpscale"].setdefault(rootbase, {})
                pkgname = d
                importedpkgstr = "jumpscale.{}.{}".format(rootbase, pkgname)
                __all__.append(importedpkgstr)
                # print("import: ", importedpkgstr)
                # globals()[importedpkgstr] = lazy_import.lazy_module(importedpkgstr)
                try:
                    m = importlib.import_module(importedpkgstr)
                except Exception as e:
                    traceback.print_exception(*sys.exc_info())
                    print("[-] {} at {} ".format(e, importedpkgstr))
                    continue
                else:
                    if hasattr(m, "export_module_as"):
                        # print("rootbase: ", rootbase, importedpkgstr)
                        # print(m.export_module_as)
                        loadeddict["jumpscale"][rootbase][pkgname] = m.export_module_as
                        # loadeddict[importedpkgstr] = m.export_module_as
                    else:
                        loadeddict["jumpscale"][rootbase][pkgname] = m

    return loadeddict


class Group:
    def __init__(self, d):
        self.d = d
        for k, v in d.items():
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
        return list(self.__loaded_dict["jumpscale"].keys()) + ["config", "exceptions", "logger"]

    @property
    def logger(self):
        return self.__loaded_dict["jumpscale"]["core"]["logging"].logger

    @property
    def config(self):
        return self.__loaded_dict["jumpscale"]["core"]["config"]

    @property
    def exceptions(self):
        return self.__loaded_dict["jumpscale"]["core"]["exceptions"]

    def reload(self):
        self.__loaded = False
        self.__loaded_dict = {}

    def _load(self):
        if not self.__loaded:
            self.__loaded_dict = load()

    def __getattr__(self, name):
        self._load()

        d = self.__loaded_dict["jumpscale"][name]
        return Group(d)


j = J()
class Container:

    def install(self, name="jsng", image="threefoldtech/js-ng:latest", ports=None, volumes=None, devices=None, identity=None):
        """Creates a docker container with jsng installed on it and ready to use
        
        Keyword Arguments:
            name {str} -- Name of the new docker container (default: {"jsng"})
            image {str} -- which image you want to use (should be first contains docker) (default: {"threefoldtech/js-ng:latest"})
            ports {dict} -- ports The port number, as an integer. For example, 
                - {'2222/tcp': 3333} will expose port 2222 inside the container as port 3333 on the host. (default: {None})
            volumes volumes (dict or list) –
                A dictionary to configure volumes mounted inside the container. The key is either the host path or a volume name, and the value is a dictionary with the keys:
                bind The path to mount the volume inside the container
                mode Either rw to mount the volume read/write, or ro to mount it read-only.
                example 
                {'/home/user1/': {'bind': '/mnt/vol2', 'mode': 'rw'},
                '/var/www': {'bind': '/mnt/vol1', 'mode': 'ro'}}
            devices {list} –
                Expose host devices to the container, as a list of strings in the form <path_on_host>:<path_in_container>:<cgroup_permissions>.
                For example, /dev/sda:/dev/xvda:rwm allows the container to have read-write access to the host’s /dev/sda via a node named /dev/xvda inside the container.
            identity {str} - string contains private key
        
        Raises:
            j.exceptions.NotFound: [description]
        """        
        client = j.clients.docker.get("container_install")
        try:
            cotainer = client.get(name)
            raise j.exceptions.NotFound(f"docker with name: {name} already exists, try another name")
        except docker.errors.NotFound:
            pass
        container = client.run(name, image, entrypoint="/sbin/my_init", ports=ports, volumes=volumes, devices=None)
        if identity:
            cmd = f"""/bin/sh -c 'echo "{identity}" > /root/.ssh/id_rsa ; chmod 600 /root/.ssh/id_rsa' """
            container.exec_run(cmd)
container = Container()
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
