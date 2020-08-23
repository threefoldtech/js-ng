"""
This module exposes a j object, which contains a reference to all sub namespaces and modules available under jumpscale

It creates a container classes/types dynamically, inject attributes into these classes with references to sub namespaces and modules,
and at the end, create an instance from this container class.
"""
import importlib
import os
import sys
import types

import jumpscale


def get_container_type(full_name: str) -> type:
    """
    get a new type to be used as a container

    Args:
        full_name (str): full name to distinguish from other types.

    Returns:
        type: a new type

    """
    cls_name = "".join([name.capitalize() for name in full_name.split(".")])
    return type(cls_name, (object,), {"__fullname": full_name,})


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


def expose_all(root_module: types.ModuleType, container_type: type):
    """
    exposes all sub-modules and namespaces to be available under given container type (class)

    Args:
        root_module (types.ModuleType): module
        ns_type (type): namepace type (class)
    """

    for path in root_module.__path__:
        for name in os.listdir(path):
            if not os.path.isdir(os.path.join(path, name)) or name == "__pycache__" or name.startswith("_"):
                continue

            lazy_import_property = get_lazy_import_property(name, root_module, container_type)
            setattr(container_type, name, lazy_import_property)


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

# if the alert system is enabled, register it as an error handler
alerts_config = j.config.get("alerts")
if alerts_config and alerts_config.get("enabled"):
    level = alerts_config.get("level", 40)
    j.tools.errorhandler.register_handler(j.tools.alerthandler.alert_raise, level=level)

# Catch any exception and handle it using the error handler
sys.excepthook = j.tools.errorhandler.excepthook
