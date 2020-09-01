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
    json_str = """{
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
    json_load = j.data.serializers.json.loads(json_str)
    assert isinstance(json_load, dict)
    assert json_load["firstName"] == "John"
    assert json_load["address"]["postalCode"] == 10021
    json_dump = j.data.serializers.json.dumps(json_load)
    assert isinstance(j.data.serializers.json.dumps(json_load), str)

    file_path = "/tmp/test.json"
    j.sals.fs.write_file(file_path, json_str)
    json_load_from_file = j.data.serializers.json.load_from_file(file_path)
    assert json_load_from_file == json_load

    j.data.serializers.json.dump_to_file(file_path, json_load)
    json_dump_file = j.sals.fs.read_file(file_path)
    assert json_dump_file == json_dump

    j.sals.fs.rmtree(file_path)


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
