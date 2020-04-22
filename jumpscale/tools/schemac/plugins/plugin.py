from .utils import convert_url_to_class_name


class Plugin:
    def __init__(self, parsed_schema, schema_text):
        self._parsed_schema = parsed_schema
        self._schema_text = schema_text

    @property
    def generated_class_name(self):
        return convert_url_to_class_name(self._parsed_schema.url)

    @property
    def generated_properties(self):
        #  ipdb> (c._parsed_schema.props['lobjs'])
        # {'index': False, 'index_key': False, 'index_text': False, 'unique': False, 'type': <jumpscale.data.
        # types.types.List object at 0x7f03f61b95d0>, 'comment': '', 'defaultvalue': '7amada.test', 'name': '
        # lobjs', 'pointer_type': '7amada.test', 'prop_type': 'LO'}
        # ipdb> (c._parsed_schema.props['objs'])
        # *** KeyError: 'objs'
        # ipdb> (c._parsed_schema.props['obj'])
        # {'index': False, 'index_key': False, 'index_text': False, 'unique': False, 'type': <jumpscale.data.types.types.JSObject object at 0x7f03f61b92d0>, 'comment': '', 'defaultvalue': '7mada.test', 'name': 'obj', 'pointer_type': '7mada.test', 'prop_type': 'O'}

        return self._parsed_schema.props

    def generate(self):
        pass
