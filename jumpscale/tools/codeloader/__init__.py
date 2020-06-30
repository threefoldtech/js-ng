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

import os
import sys
import importlib


def load_python_module(module_path: str):
    """Loads python module by module path

    Arguments:
        module_path {str} -- absolute path of the module
    """
    from jumpscale.loader import j

    module_uid = module_path[:-3]
    module_name = j.sals.fs.stem(module_path)
    spec = importlib.util.spec_from_file_location(module_name, module_path)

    if module_uid in sys.modules:
        return sys.modules[module_uid]

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_uid] = module
    spec.loader.exec_module(module)

    return module
