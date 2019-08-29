from redis import Redis
import json
from jumpscale.data.bcdb import models as models
from .clients import *

class BCDB:
    def __init__(self, ns):
        self.ns = ns
        self.storage = RedisStorageClient(ns)
        self.indexer = RedisIndexClient(ns)
        self.indexer_set = SQLiteIndexSetClient(ns)
        self.indexer_text = SonicIndexTextClient(ns)
        self.models = {
            
        }
        self.loaded_models = {

        }
        self.detect_models()
        self.model_model = self.models["model"](self)

    def detect_models(self):
        for model_name in dir(models):
            model = getattr(models, model_name)
            if isinstance(model, type) and issubclass(model, models.ModelBase):
                self.models[model._name] = model
    
    def save_obj(self, model, obj):
        self.indexer_set.set(model, obj)
        self.indexer_text.set(model, obj)
        for prop in model.schema.props.values():
            old_obj = model.get_by('id', obj.id)
            prop_name = prop.name
            index_prop = getattr(obj, prop.name)
            old_index = getattr(old_obj, prop.name) if old_obj else None
            if prop.index:
                self.indexer.set(model, prop_name, index_prop, obj.id, old_index)
        self.storage.set(model, obj.id, obj)

    def model_id_incr(self, model):
        return self.storage.incr_id(model)

    def get_item_by_id(self, model, id):
        return self.storage.get(model, id)

    def get_entry(self, model, key, val):
        if key not in model.schema.props:
            raise RuntimeError(f"{key} is not a part of {model.name}'s schema")
        if model.schema.props[key].index:
            return self.get_item_from_index(model, key, val)
        elif model.schema.props[key].index_key:
            found = self.get_item_from_index_set(model, key, val, val)
            return found[0] if found else None
        else:
            for obj in self.storage.get_keys_in_model(model):
                if getattr(obj, key) == val:
                    return obj
        return None

    def get_range(self, model, key, min, max):
        if key not in model.schema.props:
            raise RuntimeError(f"{key} is not a part of {model.name}'s schema")
        if not model.schema.props[key].index_key:
            return self.get_item_from_index_set(model, key, min, max)
        else:
            result = []
            for obj in self.storage.get_keys_in_model(model):
                    obj_val = getattr(obj, key)
                    if obj_val >= min and obj_val <= max:
                        result.append(obj)
            return result
            

    def get_item_from_index(self, model, key, val):
        if key not in model.schema.props:
            raise RuntimeError(f"{key} is not a part of {model.name}'s schema")
        if not model.schema.props[key].index:
            raise RuntimeError(f"{key} is not indexed.")
        keyid = self.indexer.get(model, key, val)
        return self.get_item_by_id(model, keyid) if keyid else None

    def get_item_from_index_set(self, model, key, min, max):
        if key not in model.schema.props:
            raise RuntimeError(f"{key} is not a part of {model.name}'s schema")
        if not model.schema.props[key].index_key:
            raise RuntimeError(f"{key} is not indexed.")
        return [self.get_item_by_id(model, x[0]) for x in self.indexer_set.get(model, key, min, max)]
        

    def get_item_from_index_text(self, model, key, pattern):
        return [self.get_item_by_id(model, int(x)) for x in self.indexer_text.get(model, key, pattern)]

    def get_model_by_name(self, model_name):
        if model_name not in self.loaded_models:
            if model_name not in self.models:
                raise RuntimeError("Model not registered")
            self.loaded_models[model_name] = self.models[model_name](self)
        return self.loaded_models[model_name]
