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
    "LO": "[] of ",
}


TEMPLATE = """
# GENERATED CLASS DON'T EDIT
class {{generated_class_name}}
{%- for prop in generated_properties.values() %}
    {%- if prop %}
        {%- if prop.defaultvalue and prop.prop_type[0] not in ['L', 'O'] %}
        property {{prop.name}} = {{prop.defaultvalue}}    
        {%- elif prop.prop_type == "O" %}
        property {{prop.name}} : {{prop.url_to_class_name}}
        {%- elif prop.prop_type == "L" and not prop.defaultvalue %}
        property {{prop.name}} : [] of Object
        {%- elif prop.prop_type == "L" and prop.defaultvalue %}
        property {{prop.name}} = {{types_map[prop.prop_type]}}
        {%- elif prop.prop_type == "LO" and prop.defaultvalue %}
        property {{prop.name}} : [] of {{prop.url_to_class_name}}
        {%- elif prop.prop_type == "LO" and not prop.defaultvalue %}
        property {{prop.name}} : [] of Object

        {%- elif prop.prop_type[0] == 'L' and prop.prop_type[1] != 'O' %}
        property {{prop.name}} : {{types_map[prop.prop_type]}}
        {%- else %}
        property {{prop.name}} : {{types_map[prop.prop_type]}}
        {%- endif %}
    {%- endif %}
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
        )
        return j.tools.jinja2.render_template(template_text=TEMPLATE, **data)
