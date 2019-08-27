from redis import Redis
import json
from jumpscale.data.bcdb import models as models
from .clients import *

class BCDB:
    def __init__(self, ns, storage, indexer, indexer_set, indexer_text):
        self.ns = ns
        self.storage = RedisStorageClient(ns)
        self.indexer = RedisIndexClient(ns)
        self.indexer_set = indexer_set
        self.indexer_text = indexer_text
        self.model_model = models.ModelModel(self, "model") 
        self.loaded_models = {
            "model": self.model_model
        }

    def save_obj(self, model, obj):
        prop_name = self._get_prop_name(model.name, obj.id)
        for prop in model.schema.props.values():
            if prop.index:
                prop_name = prop.name
                index_prop = getattr(obj, prop.name)
                old_obj = model.get_by('id', obj.id)
                old_index = getattr(old_obj, prop.name)
                print(old_index)
                self.indexer.set(model, prop_name, index_prop, obj.id, old_index)
        self.storage.set(model, obj.id, obj)

    def _get_prop_name(self, name, id):
        return f"{self.ns}.{name}://{id}"
    
    def model_id_incr(self, name):
        model_id_prop = f"{self.ns}.{name}.lastid"
        return self.storage.incr_id(model_id_prop)

    def get_item_by_id(self, model, id):
        return self.storage.get(model, id)

    def get_item_from_index(self, model, key, val):
        keyid = self.indexer.get(model, key, val)
        return self.get_item_by_id(model, keyid)

    def get_item_from_index_set(self, model, key, min, max):
        pass
        # keys = self.storage.keys()
        # found = []
        # for db_key in keys:
        #     if db_key.startswith(f"{self.ns}.{model.name}://".encode()):
        #         loaded_obj = model.load_obj_from_dict(json.loads(self.storage.get(db_key)))
        #         targeted_value = getattr(loaded_obj, key)
        #         if targeted_value >= min and targeted_value <= max:
        #             found.append(loaded_obj)
        # return found

    def get_item_from_index_text(self, model, key, pattern):
        pass
    #     keys = self.storage.keys()
    #     found = []
    #     for db_key in keys:
    #         if db_key.startswith(f"{self.ns}.{model.name}://".encode()):
    #             loaded_obj = model.load_obj_from_dict(json.loads(self.storage.get(db_key)))
    #             targeted_value = getattr(loaded_obj, key)
    #             if pattern in targeted_value:
    #                 found.append(loaded_obj)
    #     return found

    def get_model_by_name(self, model_name):
        if model_name not in self.loaded_models:
            schema = self.get_item_from_index(self.model_model, "name", model_name)
            if schema is None:
                raise RuntimeError("Schema not registered")
            self.loaded_models[model_name] = getattr(models, schema.model_class)(self, model_name)
        return self.loaded_models[model_name]

    def get_model_by_schema_id(self, schema_id):
        """
        prop_name = self._get_prop_name("schema", schema_id)
        schema_desc = self.storage.get(prop_name)
        if schema_desc is None:
                raise RuntimeError("Schema not registered")
        schema = self.model_model.load_obj_from_dict(json.loads(schema_desc))
        if schema.name not in self.loaded_models:
            self.loaded_models[schema.name] = getattr(models, schema.model_class)(self)
        return self.loaded_models[schema.name]
        """