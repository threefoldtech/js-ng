import os
import sys
import importlib


def load_python_module(module_path: str):
    """Loads python module
    
    Arguments:
        module_path {str} -- absolute path of the module
    """
    module_name = module_path[:-3]
    spec = importlib.util.spec_from_file_location(module_name, module_path)

    if spec.name in sys.modules:
        return sys.modules[spec.name]
    
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    return module
