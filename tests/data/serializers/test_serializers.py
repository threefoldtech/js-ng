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