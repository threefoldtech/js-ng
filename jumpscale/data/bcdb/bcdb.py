from redis import Redis
import json
from jumpscale.data.bcdb import models as models

class BCDB:
    def __init__(self, ns, storage, indexer, indexer_set, indexer_text):
        self.ns = ns
        self.storage = Redis()
        self.indexer = indexer
        self.indexer_set = indexer_set
        self.indexer_text = indexer_text
        self.schema_model = models.SchemaModel(self) 
        self.loaded_models = {
            "schema": self.schema_model
        }

    
    def save_obj(self, model, obj):
        prop_name = self._get_prop_name(model.url, obj.id)
        self.storage.set(prop_name, json.dumps(model.get_dict(obj)))

    def _get_prop_name(self, url, id):
        return f"{self.ns}.{url}://{id}"
    
    def model_id_incr(self, url):
        model_id_prop = f"{self.ns}.{url}.lastid"
        return self.storage.incr(model_id_prop)

    def get_item_from_index(self, model, key, val):
        keys = self.storage.keys()
        for db_key in keys:
            if db_key.startswith(f"{self.ns}.{model.url}://".encode()):
                loaded_obj = model.load_obj_from_dict(json.loads(self.storage.get(db_key)))
                if getattr(loaded_obj, key) == val:
                    return loaded_obj
        return None
    
    def get_item_from_index_set(self, model, key, min, max):
        keys = self.storage.keys()
        found = []
        for db_key in keys:
            if db_key.startswith(f"{self.ns}.{model.url}://".encode()):
                loaded_obj = model.load_obj_from_dict(json.loads(self.storage.get(db_key)))
                targeted_value = getattr(loaded_obj, key)
                if targeted_value >= min and targeted_value <= max:
                    found.append(loaded_obj)
        return found

    def get_item_from_index_text(self, model, key, pattern):
        keys = self.storage.keys()
        found = []
        for db_key in keys:
            if db_key.startswith(f"{self.ns}.{model.url}://".encode()):
                loaded_obj = model.load_obj_from_dict(json.loads(self.storage.get(db_key)))
                targeted_value = getattr(loaded_obj, key)
                if pattern in targeted_value:
                    found.append(loaded_obj)
        return found

    def get_model_by_schema_url(self, schema_url):
        if schema_url not in self.loaded_models:
            schema = self.get_item_from_index(self.schema_model, "url", schema_url)
            if schema is None:
                raise RuntimeError("Schema not registered")
            self.loaded_models[schema_url] = getattr(models, schema.model_class)(self)
        return self.loaded_models[schema_url]

    def get_model_by_schema_id(self, schema_id):
        prop_name = self._get_prop_name("schema", schema_id)
        schema_desc = self.storage.get(prop_name)
        if schema_desc is None:
                raise RuntimeError("Schema not registered")
        schema = self.schema_model.load_obj_from_dict(json.loads(schema_desc))
        if schema.url not in self.loaded_models:
            self.loaded_models[schema.url] = getattr(models, schema.model_class)(self)
        return self.loaded_models[schema.url]