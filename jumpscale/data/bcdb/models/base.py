from jumpscale.god import j

class JSObjBase:
    def __init__(self):
        pass

    

class ModelBase:
    _schema = ""
    def __init__(self, bcdb):
        self.schema = self._load_schema()
        self.bcdb = bcdb
        self.url = self.schema.system_props["url"]

    def _load_schema(self):
        return j.data.schema.parse_schema(self._schema)
    
    def create_obj(self, **kwargs):
        o = JSObjBase()
        self.set_from_dict(o, kwargs)
        return o

    def save_obj(self, obj):
        self.bcdb.save_obj(obj)

    def _incr_id(self):
        return self.bcdb.model_id_incr(self.url)
    
    def get_by(self, key, value):
        return self.bcdb.get_prop_from_index(self.url, key, value)

    def get_range(self, key, min, max):
        return self.bcdb.get_prop_from_index_set(self.url, key, min, max)
    
    def get_pattern(self, key, pattern):
        return self.bcdb.get_prop_from_index_text(self.url, key, pattern)
    
    def get_dict(self, obj):
        d = {}
        for prop in self.schema.props:
            prop_name = prop.name
            d[prop_name] = getattr(obj, prop_name)
        return d

    def set_from_dict(self, d, o):
        for prop in self.schema.props:
            prop_name = prop.name
            if prop_name in kwargs:
                if not prop.check(kwatgs[prop_name])
                    raise ValueError("Wrong form")
                setattr(o, prop, kwargs[prop_name])
            else:
                setattr(o, prop, prop.defaulvalue)
        return o

    def get_url(self):
        return self.url
