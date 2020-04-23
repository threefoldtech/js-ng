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
}


def get_prop_line(prop):
    prop_type = prop.prop_type
    python_type = types_map.get(prop_type)
    line = f"{prop.name} = "

    # print(f"\n\n{prop.name} => {prop} \n\n")
    # primitive with a default or not.

    if prop_type == "O":
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


TEMPLATE = """
#GENERATED CLASS DONT EDIT
from jumpscale.core.base import Base, fields


class {{generated_class_name}}(Base):
{%- for prop in generated_properties.values() %}
    {{get_prop_line(prop)}}
{%- endfor %}

"""


class JSNGGenerator(Plugin):
    def __init__(self, parsed_schema, schema_text):
        super().__init__(parsed_schema, schema_text)

    def generate(self):
        data = dict(
            generated_class_name=self.generated_class_name,
            generated_properties=self.generated_properties,
            types_map=types_map,
            get_prop_line=get_prop_line,
        )
        return j.tools.jinja2.render_template(template_text=TEMPLATE, **data)
