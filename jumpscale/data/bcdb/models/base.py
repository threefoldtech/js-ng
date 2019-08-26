from jumpscale.god import j

class JSObjBase:
    def __init__(self, schema, model, **kwargs):
        pass

    def get_dict(self):
        pass
    
    def set_from_dict(self):
        pass
    
    def save(self):
        pass
    
    def get_url(self):
        return self.model.url

    

class ModelBase:
    _schema = ""
    def __init__(self, bcdb):
        self.schema = self._load_schema()
        self.bcdb = bcdb
        self.url = self.schema.system_props["url"]

    def _load_schema(self):
        return j.data.schema.parse_schema(self._schema)
    
    def create_obj(self, **kwargs):
        return JSObjBase(self.schema, self, **kwargs)

    def save_obj(self, obj):
        self.bcdb.save_obj(obj)

    def _incr_id(self):
        pass
    
    def get_by(self, key, value):
        pass

    def get_range(self, key, min, max):
        pass
    
    def get_pattern(self, key, pattern):
        pass
    