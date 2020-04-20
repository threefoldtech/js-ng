"""
This module exposes a j object, which contains a reference to all sub namespaces and modules available under jumpscale

It creates a container classes/types dynamically, inject attributes into these classes with references to sub namespaces and modules,
and at the end, create an instance from this container class.
"""
import importlib
import os
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


def get_new_property(name: str, module: types.ModuleType) -> property:
    """
    get a new property that returns this module, so, it is not loaded until it's accessed

    Args:
        name (str): module name
        module (type): module

    Returns:
        property: a new property for this module
    """
    inner_name = f"__{name}"

    def getter(self):
        if hasattr(self, inner_name):
            return getattr(self, inner_name)

        if hasattr(module, "export_module_as"):
            new_module = module.export_module_as()
        else:
            new_module = module

        setattr(self, inner_name, new_module)
        return new_module

    return property(fget=getter)


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

            full_name = f"{root_module.__name__}.{name}"
            mod = importlib.import_module(full_name)
            if mod.__spec__.origin == "namespace":
                # if this module is a namespace, create a new container type
                # then do the same with it
                sub_container_type = get_container_type(full_name)
                expose_all(mod, sub_container_type)

                # after that, just set an instance of this container type
                # as an attribute
                setattr(container_type, name, sub_container_type())
            else:
                # if it's just a module, set it as a property attribute
                setattr(container_type, name, get_new_property(name, mod))


Jumpscale = get_container_type("Jumpscale")
expose_all(jumpscale, Jumpscale)
j = Jumpscale()
