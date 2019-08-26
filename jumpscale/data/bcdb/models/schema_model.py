from jumpscale.god import j

from jumpscale.data.bcdb.models.base import ModelBase, JSObjBase

class SchemaModel(ModelBase):
    _schema = """
    @url = schema
    definition = "" (S)
    """

    def save_model(self, file_name, class_definition):
        self.bcdb.add_model(file_name, class_definition)

class SchemaObj(JSObjBase):
    def __init__(self, schema, model, **kwargs):
        super().__init__(schema, model, **kwargs)
        if "definition" not in kwargs:
            raise RuntimeError("schema definition must be supplied.")
        self.parsed_schema = j.data.schema.parse_schema(self.definition)

        
    def generate_model(self):
        schema_url = self.parsed_schema.urll
        model_class = self._schema_url_to_class_name(schema_url) + "Model"
        model_object_class = model_class + "Obj"
        file_name = schema_url.replace('.', '_') + "_model.py"
        schema_definition = self.definition
        class_definition = f'''
from .base import ModelBase, JSObjBase

class {model_class}(ModelBase):
    _schema = """"
    {schema_definition}
    """

class {model_object_class}(JSObjBase):
    pass

'''
        self.model.save_model(file_name, class_definition)
    
    def _schema_url_to_class_name(self, schema_url):
        assert _valid_url(schema_url)
        res = ""
        l = len(schema_url)
        for i in range(len(schema_url)):
            if i + 1 < l and schema_url[i + 1] == '.' or i == 0:
                res += schema_url[i].capitalize()
            elif schema_url[i] != '.':
                res += schema_url[i]
        return res

    def _valid_url(self, schema_url):
        if not schema_url[0].isalnum() or not schema_url[-1].isalnum():
            return False
        for i in range(len(schema_url)):
            if i and schema_url[i] == schema_url[i - 1] and schema_url[i] == '.':
                return False
            if not schema_url[i].isalnum() and schema_url[i] != '.':
                return False
        return True