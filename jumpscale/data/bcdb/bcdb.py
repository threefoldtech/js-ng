from redis import Redis
import json
# import jumpscale.data.bcdb.models as models

class BCDB:
    def __init__(self, ns, storage, indexer, indexer_set, indexer_text):
        self.ns = ns
        self.storage = Redis()
        self.indexer = indexer
        self.indexer_set = indexer_set
        self.indexer_text = indexer_text
    
    def save(self, obj):
        prop_name = f"{self.ns}.{obj.get_url()}://{obj.id}"
        self.storage.set(prop_name, json.dumps(obj.get_dict()))

    def add_model(self, file_name, model_definition):
        with open(f"models/{file_name}", "w+") as fd:
            fd.write(model_definition)
 
