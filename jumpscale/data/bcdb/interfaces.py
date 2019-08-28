class StorageInterface:
    def get(self, model, obj_id):
        pass
    
    def set(self, model, obj_id, value):
        pass

class IndexInterface:
    def get(self, model, index_prop, index_value):
        pass

    def set(self, model, index_prop, index_value, old_value=None):
        pass

class IndexSetInterface:
    def get(self, model, index_prop, index_min, index_max):
        pass

    def set(self, model, obj):
        pass

class IndexTextInterface:
    def get(self, model, index_prop, pattern):
        pass
    
    def set(self, model, index_prop, index_value, old_value=None):
        pass

class SerializerInterface:
    def loads(self, model, s):
        pass

    def dumps(self, model, data):
        pass