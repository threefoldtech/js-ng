import pytest
import base64
import pylzma
import msgpack
import yaml
import pickle
from jumpscale.loader import j


def test_base64():
    assert j.data.serializers.base64.encode("omar") == base64.b64encode("omar".encode())
    assert j.data.serializers.base64.encode(b"omar") == base64.b64encode(b"omar")
    assert j.data.serializers.base64.decode("omar") == base64.b64decode("omar".encode())
    assert j.data.serializers.base64.decode(b"omar") == base64.b64decode(b"omar")


def test_pickle():
    obj = pickle.dumps(b"omar")
    assert j.data.serializers.pickle.compress(b"omar") == obj
    assert j.data.serializers.pickle.decompress(obj) == pickle.loads(obj)


def test_json():
    jsonstr = """{
        "firstName": "John",
        "lastName": "Smith",
        "address": {
            "streetAddress": "21 2nd Street",
            "city": "New York",
            "state": "NY",
            "postalCode": 10021
        },
        "phoneNumbers": [
            "212 555-1234",
            "646 555-4567"
        ]
    }
    """
    jsondict = j.data.serializers.json.loads(jsonstr)
    assert isinstance(jsondict, dict)
    assert isinstance(j.data.serializers.json.dumps(jsondict), str)


def test_lzma():
    obj = pylzma.compress(b"omar")
    assert j.data.serializers.lzma.compress(b"omar") == obj
    assert j.data.serializers.lzma.decompress(obj) == pylzma.decompress(obj)


def test_msgpack():
    obj = msgpack.packb(b"omar", use_bin_type=True)
    assert j.data.serializers.msgpack.dumps(b"omar") == obj
    assert j.data.serializers.msgpack.loads(obj) == msgpack.unpackb(obj, raw=False)
    assert j.data.serializers.msgpack.loads("omar") == False


def test_toml():
    tomlstr = """title = "config"
   [feature1]
   enable = true
   userids = [
     "12345", "67890"
   ]

   [feature2]
   enable = false
   """
    tomldict = j.data.serializers.toml.loads(tomlstr)
    assert isinstance(tomldict, dict)
    assert isinstance(j.data.serializers.toml.dumps(tomldict), str)


def test_yaml():
    yamstr = """Section:
    heading: Heading 1
    font:
        name: Times New Roman
        size: 22
        color_theme: ACCENT_2

SubSection:
    heading: Heading 3
    font:
        name: Times New Roman
        size: 15
        color_theme: ACCENT_2
Paragraph:
    font:
        name: Times New Roman
        size: 11
        color_theme: ACCENT_2
Table:
    style: MediumGrid3-Accent2
"""

    yamldict = j.data.serializers.yaml.loads(yamstr)
    assert isinstance(yamldict, dict)
    assert isinstance(j.data.serializers.yaml.dumps(yamldict), str)
