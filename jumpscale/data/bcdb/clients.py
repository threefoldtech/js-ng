from .interfaces import *
from redis import Redis
import json

class JSONSerializer(SerializerInterface):
    def loads(self, model, s):
        return model.load_obj_from_dict(json.loads(s))
        
    def dumps(self, model, data):
        return json.dumps(model.get_dict(data))

class RedisStorageClient(StorageInterface):
    def __init__(self, bcdb_namespace, host="localhost", port=6379, serializer=None):
        self.redis_client = Redis(host=host, port=port)
        self.serializer = serializer or JSONSerializer()
        self.bcdb_namespace = bcdb_namespace

    def get(self, model, obj_id):
        return self.serializer.loads(model, self.redis_client.get(f"{self.bcdb_namespace}.{model.name}://{obj_id}"))
    
    def set(self, model, obj_id, value):
        return self.redis_client.set(f"{self.bcdb_namespace}.{model.name}://{obj_id}", self.serializer.dumps(model, value))
    
    def incr_id(self, model):
        return self.redis_client.incr(f"{self.bcdb_namespace}.{model.name}.lastid")

class RedisIndexClient(IndexInterface):
    def __init__(self, bcdb_namespace, host="localhost", port=6379):
        self.redis_client = Redis(host=host, port=port)
        self.bcdb_namespace = bcdb_namespace

    def get(self, model, index_prop, index_value):
        return int(self.redis_client.get(f"{self.bcdb_namespace}.indexer.{model.name}.{index_prop}://{index_value}"))

    def set(self, model, index_prop, index_value, obj_id, old_value=None):
        if old_value:
            self.redis_client.delete(f"{self.bcdb_namespace}.indexer.{model.name}.{index_prop}://{old_value}")
        return self.redis_client.set(f"{self.bcdb_namespace}.indexer.{model.name}.{index_prop}://{index_value}", obj_id)
