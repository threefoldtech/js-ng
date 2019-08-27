from jumpscale.god import j

from .base import ModelBase, JSObjBase

class SchemaModel(ModelBase):
    _schema = """
    @url = schema
    model_class = "" (S)
    url = "" (S)
    """