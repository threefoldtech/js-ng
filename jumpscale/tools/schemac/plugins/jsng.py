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


TEMPLATE = """
#GENERATED CLASS DON'T EDIT
from jumpscale.core.base import Base, fields


class {{generated_class_name}}(Base):
{%- for prop in generated_properties.values() %}
    {%- if prop %}
    {%- if prop.prop_type[0] != 'L' %}
    {{prop.name}} = fields.{{types_map[prop.prop_type]}}()
    {%- else %}
    {{prop.name}} = fields.{{types_map[prop.prop_type]}}(fields.{{types_map[prop.prop_type[1]]}}())
    {%- endif %}
    {%- endif %}
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
        )
        return j.tools.jinja2.render_template(template_text=TEMPLATE, **data)
