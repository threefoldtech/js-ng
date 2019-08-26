from jumpscale.god import j

from jumpscale.data.bcdb.models.base import ModelBase, JSObjBase

class SchemaModel(ModelBase):
    _schema = """
    @url = schema
    modelclass = "" (S)
    url = "" (S)
    """