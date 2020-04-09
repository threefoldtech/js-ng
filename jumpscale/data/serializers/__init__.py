"""This module does all the work for serialization/deserialization around pickle, base64, json, msgpack, pickle, dill, toml
```
JS-NG> obj = {"name":"username", "list":[1,3,4,7], "n":5}                                           

JS-NG> j.data.serializers.json.dumps(obj)                                                           
'{"name": "username", "list": [1, 3, 4, 7], "n": 5}'

JS-NG> j.data.serializers.toml.dumps(obj)                                                           
'name = "username"\nlist = [1, 3, 4, 7]\nn = 5\n'

JS-NG> j.data.serializers.yaml.dumps(obj)                                                           
'list:\n- 1\n- 3\n- 4\n- 7\nn: 5\nname: username\n'

JS-NG> j.data.serializers.msgpack.dumps(obj)                                                        
b'\x83\xa4name\xa8username\xa4list\x94\x01\x03\x04\x07\xa1n\x05'
```
"""

from . import base64
from . import json
from . import lzma
from . import msgpack
from . import pickle
from . import toml
from . import yaml
from . import dill
