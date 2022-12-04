"""Loads a module from path

Let's make sure we have a python module in path `/tmp/hello.py`
```
~> cat /tmp/hello.py
a = 5
b = 6
z = a+b
```

## Using the codeloader tool

```python
JS-NG> m = j.tools.codeloader.load_python_module("/tmp/hello.py")
JS-NG> m.a
5
```

"""
import importlib
import os
import sys
import types

from jumpscale.sals.fs import stem


def load_python_module(module_path: str, force_reload: bool = False) -> types.ModuleType:
    """
    Loads python module by path

    Args:
        module_path (str): absolute path of the module
        force_reload (bool, optional): will reload the module if set. Defaults to False.

    Returns:
        types.ModuleType: module object
    """
    module_uid = module_path[:-3]
    module_name = stem(module_path)
    spec = importlib.util.spec_from_file_location(module_name, module_path)

    if module_uid in sys.modules and not force_reload:
        return sys.modules[module_uid]

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_uid] = module
    spec.loader.exec_module(module)

    return module
