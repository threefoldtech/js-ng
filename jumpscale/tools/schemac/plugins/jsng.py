from .plugin import Plugin
from jumpscale.god import j

types_map = {
    "": "String",
    "S": "String",
    "O": "Object",
    "I": "Integer",
    "F": "Float",
    "B": "Boolean",
    "L": "List",
    "LS": "List",
    "LI": "List",
    "LF": "List",
    "LO": "List",
    "E": "Enum",
}


def get_prop_line(prop):
    prop_type = prop.prop_type
    python_type = types_map.get(prop_type)
    line = f"{prop.name} = "

    # print(f"\n\n{prop.name} => {prop} \n\n")
    # primitive with a default or not.
    if prop_type == "E":
        line += f"fields.{python_type}({prop.name.capitalize()})"
    elif prop_type == "O":
        line += f"fields.{python_type}()"
    elif prop_type == "LO" and prop.defaultvalue and prop.defaultvalue != "[]":
        line += f"fields.List(fields.Object())"
    elif prop_type == "LO" and not prop.defaultvalue:
        line += f"fields.List(fields.Object())"
    elif python_type == "L" and not prop.defaultvalue:
        line += f" fields.List(fields.Object())"
    elif python_type == "L" and prop.defaultvalue:
        line += f" fields.List(fields.Object())"
    elif len(prop_type) > 1 and prop_type[0] == "L" and prop_type[1] != "O":
        line += f"fields.{python_type}(fields.{types_map[prop_type[1:]]}())"
    elif prop_type in ["I", "F", "B"] and not prop.defaultvalue:
        line += f"fields.{python_type}()"
    elif prop_type in ["I", "F", "B"] and prop.defaultvalue:
        line += f"fields.{python_type}(default={prop.defaultvalue})"
    elif prop_type == "S":
        line += f'fields.String(default="{prop.defaultvalue}")'
    else:
        line += f"fields.{python_type}()"

    return line


SINGLE_TEMPLATE = """

class {{generated_class_name}}(Base):
{%- for prop in generated_properties.values() %}
    {{get_prop_line(prop)}}
{%- endfor %}

"""

TEMPLATE = """
#GENERATED CLASS DONT EDIT
from jumpscale.core.base import Base, fields
from enum import Enum

{%- for enum in enums %}

class {{enum['name']}}(Enum):
    {%- for enumval in enum['vals'] %}
    {{enumval}} = {{loop.index0}}
    {%- endfor %}
{%- endfor %}

{{classes_generated}}

"""


class JSNGGenerator(Plugin):
    def __init__(self):
        super().__init__()

        self._single_template = SINGLE_TEMPLATE
        self._template = TEMPLATE
        self._get_prop_line = get_prop_line
        self._types_map = types_map
