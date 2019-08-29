from jumpscale.god import j
from jumpscale.data.schema import Property
from jumpscale.data.types import Integer, JSObject
import json

class JSObjBase:
    def __init__(self, model):
        self.model = model

    def get_dict(self):
        return self.model.get_dict(self)

    def save(self):
        return self.model.save_obj(self)

    def __str__(self):
        return json.dumps(self.get_dict(), indent=4)

class ModelBase:
    _schema = ""
    _name = ""
    def __init__(self, bcdb):
        self.schema = self._load_schema()
        self.schema.props["id"] = Property()
        self.schema.props["id"].unique = True
        self.schema.props["id"].index = True
        self.schema.props["id"].type = Integer()
        self.schema.props["id"].name = "id"
        
        self.bcdb = bcdb
        self.name = self._name

    def _load_schema(self):
        return j.data.schema.parse_schema(self._schema)
    
    def create_obj(self, data):
        o = JSObjBase(self)
        data['id'] = self._incr_id()
        self.set_from_dict(o, data)
        return o

    def _assert_uniqueness(self, obj):
        for prop in self.schema.props.values():
            if prop.unique:
                dbobj = self.get_by(prop.name, getattr(obj, prop.name))
                if dbobj is not None and dbobj.id != obj.id:
                    raise RuntimeError(f"{prop.name} is unique. One already exists.")
    
    def save_obj(self, obj):
        self._assert_uniqueness(obj)
        self.bcdb.save_obj(self, obj)

    def _incr_id(self):
        return self.bcdb.model_id_incr(self)
    
    def get_by(self, key, value):
        return self.bcdb.get_entry(self, key, value)

    def get_range(self, key, min, max):
        return self.bcdb.get_item_from_index_set(self, key, min, max)
    
    def get_pattern(self, key, pattern):
        return self.bcdb.get_item_from_index_text(self, key, pattern)
    
    def get_dict(self, obj):
        d = {}
        for prop in self.schema.props.values():
            prop_name = prop.name
            d[prop_name] = getattr(obj, prop_name)
            if isinstance(prop.type, JSObject):
                d[prop_name] = d[prop_name].get_dict()
        return d

    def set_from_dict(self, o, d):
        # import ipdb; ipdb.set_trace()
        for prop in self.schema.props.values():
            prop_name = prop.name
            if prop_name in d:
                if not prop.type.check(d[prop_name]):
                    raise ValueError("Wrong form")
                if isinstance(prop.type, JSObject):
                    obj_model = self.bcdb.get_model_by_name(prop.defaultvalue)
                    setattr(o, prop_name, obj_model.load_obj_from_dict(d[prop_name]))
                else:
                    setattr(o, prop_name, prop.type.from_str(d[prop_name]))
            else:
                setattr(o, prop_name, prop.type.default)
        return o

    def load_obj_from_dict(self, d):
        o = JSObjBase(self)
        self.set_from_dict(o, d)
        return o
