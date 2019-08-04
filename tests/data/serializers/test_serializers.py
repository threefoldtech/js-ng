import pytest
from jumpscale.god import j

@pytest.fixture
def make_serializer():
    return j.data.serializers

def test_yaml(make_serializer):
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
    yamdict={'Section': {'heading': 'Heading 1', 'font': {'name': 'Times New Roman', 'size': 22, 'color_theme':
'ACCENT_2'}}, 'SubSection': {'heading': 'Heading 3', 'font': {'name': 'Times New Roman', 'size': 15, 'color_theme': 'ACCENT_2'}},
'Paragraph': {'font': {'name': 'Times New Roman', 'size': 11, 'color_theme': 'ACCENT_2'}}, 'Table': {'style': 'MediumGrid3-Accent2'}}
    assert type(make_serializer.dump(yamdict,'yaml'))==type('just string')
    assert type(make_serializer.load(yamstr,'yaml'))==type({'dict':'test'})

def test_toml(make_serializer):
    tomstr = """
# This is a TOML document.

 title = "TOML Example"

 [owner]
 name = "Tom Preston-Werner"
 dob = 1979-05-27T07:32:00-08:00 # First class dates

 [database]
 server = "192.168.1.1"
 ports = [ 8001, 8001, 8002 ]
 connection_max = 5000
 enabled = true

 [servers]

   # Indentation (tabs and/or spaces) is allowed but not required
   [servers.alpha]
   ip = "10.0.0.1"
   dc = "eqdc10"

   [servers.beta]
   ip = "10.0.0.2"
   dc = "eqdc10"

 [clients]
 data = [ ["gamma", "delta"], [1, 2] ]

 # Line breaks are OK when inside arrays
 hosts = [
   "alpha",
   "omega"
 ]
 """
    tomdict={'title': 'TOML Example', 'owner': {'name': 'Tom Preston-Werner',
     'dob':'none','database': {'server': '192.168.1.1', 'ports': [8001, 8001, 8002], 'connection_max': 5000, 'enabled': True},
     'servers': {'alpha': {'ip': '10.0.0.1', 'dc': 'eqdc10'}, 'beta': {'ip': '10.0.0.2', 'dc': 'eqdc10'}},
      'clients': {'data': [['gamma', 'delta'], [1, 2]], 'hosts': ['alpha', 'omega']}}}
    assert type(make_serializer.load(tomstr,'toml'))==type({'a':'b'})
    assert type(make_serializer.dump(tomdict,'toml'))==type("str")