from jumpscale.god import j
from jumpscale.data.schema import Property
from jumpscale.data.types import Integer

class JSObjBase:
    def __init__(self):
        pass

    

class ModelBase:
    _schema = ""
    def __init__(self, bcdb):
        self.schema = self._load_schema()
        self.schema.props["id"] = Property()
        self.schema.props["id"].unique = True
        self.schema.props["id"].index = True
        self.schema.props["id"].type = Integer()
        self.schema.props["id"].name = "id"
        
        self.bcdb = bcdb
        self.url = self.schema.system_props["url"]

    def _load_schema(self):
        return j.data.schema.parse_schema(self._schema)
    
    def create_obj(self, data):
        o = JSObjBase()
        data['id'] = self._incr_id()
        self.set_from_dict(o, data)
        return o

    def save_obj(self, obj):
        self.bcdb.save_obj(self, obj)

    def _incr_id(self):
        return self.bcdb.model_id_incr(self.url)
    
    def get_by(self, key, value):
        return self.bcdb.get_item_from_index(self, key, value)

    def get_range(self, key, min, max):
        return self.bcdb.get_item_from_index_set(self, key, min, max)
    
    def get_pattern(self, key, pattern):
        return self.bcdb.get_item_from_index_text(self, key, pattern)
    
    def get_dict(self, obj):
        d = {}
        for prop in self.schema.props.values():
            prop_name = prop.name
            d[prop_name] = getattr(obj, prop_name)
        return d

    def set_from_dict(self, o, d):
        for prop in self.schema.props.values():
            prop_name = prop.name
            if prop_name in d:
                if not prop.type.check(d[prop_name]):
                    raise ValueError("Wrong form")
                setattr(o, prop_name, prop.type.from_str(d[prop_name]))
            else:
                setattr(o, prop_name, prop.defaultvalue)
        return o

    def load_obj_from_dict(self, d):
        o = JSObjBase()
        self.set_from_dict(o, d)
        return o


    def get_url(self):
        return self.url
