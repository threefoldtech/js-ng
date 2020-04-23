from .plugin import Plugin
from jumpscale.god import j

types_map = {
    "": "String",
    "S": "String",
    "O": "Object",
    "I": "Int64",
    "F": "Float",
    "B": "Boolean",
    "L": "[] of Object",
    "LS": "[] of String",
    "LI": "[] of Int64",
    "LF": "[] of Float",
    "LO": "",
}


def get_prop_line(prop):
    prop_type = prop.prop_type
    crystal_type = types_map.get(prop_type)
    line = f"property {prop.name}"

    # print(f"\n\n{prop.name} => {prop} \n\n")
    # primitive with a default or not.
    if prop_type == "E":
        line += f" : {prop.name.capitalize()}"
    elif prop_type == "O":
        line += f" : {prop.url_to_class_name}"
    elif prop_type == "LO" and prop.defaultvalue and prop.defaultvalue != "[]":
        line += f" : [] of {prop.url_to_class_name}"
    elif prop_type == "LO" and not prop.defaultvalue:
        line += f" : [] of Object"
    elif crystal_type == "L" and not prop.defaultvalue:
        line += f" : [] of Object"
    elif crystal_type == "L" and prop.defaultvalue:
        line += f" = {crystal_type}"
    elif len(prop_type) > 1 and prop_type[0] == "L" and prop_type[1] != "O":
        line += f" : {crystal_type}"

    elif prop_type in ["I", "F", "B"] and not prop.defaultvalue:
        line += f" : {crystal_type}"
    elif prop_type in ["I", "F", "B"] and prop.defaultvalue:
        line += f" = {prop.defaultvalue}"
    elif prop_type == "S":
        line += f' = "{prop.defaultvalue}"'
    else:
        line += f": {crystal_type}"

    return line


TEMPLATE = """
# GENERATED CLASS DONT EDIT


{%- for enum_name, enum_vals in enums.items() %}

enum {{enum_name}}:
    {%- for enumval in enum_vals %}
    {{enumval}} = {{loop.index0}}
    {%- endfor %}
{%- endfor %}

class {{generated_class_name}}
{%- for prop in generated_properties.values() %}
    {{get_prop_line(prop)}}
{%- endfor %}

end 
"""


class CrystalGenerator(Plugin):
    def __init__(self, parsed_schema, schema_text):
        super().__init__(parsed_schema, schema_text)

    def generate(self):
        tmpl = TEMPLATE
        data = dict(
            generated_class_name=self.generated_class_name,
            generated_properties=self.generated_properties,
            types_map=types_map,
            get_prop_line=get_prop_line,
            enums=self.get_enums(),
        )
        return j.tools.jinja2.render_template(template_text=TEMPLATE, **data)
