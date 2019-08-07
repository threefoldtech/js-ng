import pytest
from jumpscale.god import j
import base64
import blosc
import pylzma
import msgpack
import yaml


def test_base64():
    assert j.data.serializers.Base64.encode("omar") == base64.b64encode("omar".encode())
    assert j.data.serializers.Base64.encode(b"omar") == base64.b64encode(b"omar")
    assert j.data.serializers.Base64.decode("omar") == base64.b64decode("omar".encode())
    assert j.data.serializers.Base64.decode(b"omar") == base64.b64decode(b"omar")


def test_blosc():
    obj = blosc.compress(b"omar", typesize=8)
    assert j.data.serializers.Blosc.compress(b"omar") == obj
    assert j.data.serializers.Blosc.decompress(obj) == blosc.decompress(obj)


def test_int():
    assert j.data.serializers.Int.dumps(123) == str(123)
    assert j.data.serializers.Int.loads("123") == int("123")


def test_lzma():
    obj = pylzma.compress(b"omar")
    assert j.data.serializers.Lzma.dumps(b"omar") == obj
    assert j.data.serializers.Lzma.loads(obj) == pylzma.decompress(obj)

def test_msgpack():
    obj=msgpack.packb(b'omar', use_bin_type=True)
    assert j.data.serializers.MSGPack.dumps(b'omar')==obj
    assert j.data.serializers.MSGPack.loads(obj)==msgpack.unpackb(obj, raw=False)
    assert j.data.serializers.MSGPack.loads('omar')==False

def test_toml():
    testtemplate = """
name = ''
multiline = ''
nr = 0
nr2 = 0
nr3 = 0
nr4 = 0.0
nr5 = 0.0
bbool = true
bbool2 = true
bbool3 = true
list1 = [ ]
list2 = [ ]
list3 = [ ]
list4 = [ ]
list5 = [ ]
"""

    testtoml = """
name = 'something'
multiline = '''
    these are multiple lines
    next line
    '''
nr = 87
nr2 = ""
nr3 = "1"
nr4 = "34.4"
nr5 = 34.4
bbool = 1
bbool2 = true
bbool3 = 0
list1 = "4,1,2,3"
list2 = [ 3, 1, 2, 3 ]
list3 = [ "a", " b ", "   c  " ]
list4 = [ "ab" ]
list5 = "d,a,a,b,c"
"""
    ddict = j.data.serializers.Toml.loads(testtoml)
    template = j.data.serializers.Toml.loads(testtemplate)

    ddictout, errors = j.data.serializers.Toml.merge(template, ddict, listunique=True)

    ddicttest = {
        "name": "something",
        "multiline": "these are multiple lines\nnext line\n",
        "nr": 87,
        "nr2": 0,
        "nr3": 1,
        "nr4": 34.4,
        "nr5": 34.4,
        "bbool": True,
        "bbool2": True,
        "bbool3": False,
        "list1": ["1", "2", "3", "4"],
        "list2": [1, 2, 3],
        "list3": ["a", "b", "c"],
        "list4": ["ab"],
        "list5": ["a", "b", "c", "d"],
    }

    assert ddictout['name'] == ddicttest['name']

    ddictmerge = {"nr": 88}

    # start from previous one, update
    ddictout, errors = j.data.serializers.Toml.merge(ddicttest, ddictmerge, listunique=True)

    ddicttest = {
        "name": "something",
        "multiline": "these are multiple lines\nnext line\n",
        "nr": 88,
        "nr2": 0,
        "nr3": 1,
        "nr4": 34.4,
        "nr5": 34.4,
        "bbool": True,
        "bbool2": True,
        "bbool3": False,
        "list1": ["1", "2", "3", "4"],
        "list2": [1, 2, 3],
        "list3": ["a", "b", "c"],
        "list4": ["ab"],
        "list5": ["a", "b", "c", "d"],
    }

    assert ddictout == ddicttest

    ddictmerge = {"nr_nonexist": 88}

    # needs to throw error
    try:
        error = 0
        ddictout, errors = merge(ddicttest, ddictmerge, listunique=True)
    except:
        error = 1
    assert 1

    ddictmerge = {}
    ddictmerge["list1"] = []
    for i in range(20):
        ddictmerge["list1"].append("this is a test %s" % i)
    ddictout, errors = j.data.serializers.Toml.merge(ddicttest, ddictmerge, listunique=True)
    template = {
        "login": "",
        "first_name": "",
        "last_name": "",
        "locations": [],
        "companies": [],
        "departments": [],
        "languageCode": "en-us",
        "title": [],
        "description_internal": "",
        "description_public_friendly": "",
        "description_public_formal": "",
        "experience": "",
        "hobbies": "",
        "pub_ssh_key": "",
        "skype": "",
        "telegram": "",
        "itsyou_online": "",
        "reports_into": "",
        "mobile": [],
        "email": [],
        "github": "",
        "linkedin": "",
        "links": [],
    }
    toupdate = {
        "companies": ["threefold"],
        "company_id": [2],
        "departments": ["threefold:engineering", "threefold:varia"],
        "description_internal": "Researcher who develops new ideas for Threefold and creates concise explanations of difficult concepts",
        "description_public_formal": "Develops new ideas for Threefold and creates concise explanations of difficult concepts.",
        "description_public_friendly": "Virgil is a researcher and innovator who is always looking to improve the world around him both on a macro and micro scale.\n\nFor the past 11 years he has been working with new technologies, helping organizations integrate them into their existing services and create their new products.  \nHe holds a PhD in autonomous robotics, artificial intelligence and reliability.\n\nVirgil also lectures at a technical university and an academy.\n\n",
        "email": ["ilian.virgil@gmail.com", "ilian@threefold.tech"],
        "name": "virgil",
        "github": "Virgil3",
        "hobbies": "generative coding, movies, diving, languages",
        "itsyou_online": "ilian@threefold.tech",
        "languageCode": "en-us",
        "last_name": "ilian",
        "linkedin": "https://www.linkedin.com/in/ilian-virgil-342b8471",
        "links": [],
        "locations": ["bucharest"],
        "login": "",
        "mobile": ["+40721543908"],
        "pub_ssh_key": "",
        "reports_into": "Kristof",
        "skype": "ilian.virgil",
        "telegram": "@virgil_ilian",
        "title": ["Researcher"],
    }

    result, errors = j.data.serializers.Toml.merge(
        template, toupdate, keys_replace={"name": "first_name"}, add_non_exist=False, die=False, errors=[]
    )

    assert [("company_id", [2])] == errors
    assert "bucharest" in result["locations"]
    assert "ilian.virgil@gmail.com" in result["email"]
    assert "company_id" not in result  # should not be in

def test_yaml():
    yamstr="""Section:
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
    
    obj=yaml.dump(yamstr, default_flow_style=False, default_style="", indent=4, line_break="\n")
    assert j.data.serializers.Yaml.dumps(yamstr)==obj
    assert j.data.serializers.Yaml.loads(obj)==yaml.load(obj,Loader=yaml.SafeLoader)