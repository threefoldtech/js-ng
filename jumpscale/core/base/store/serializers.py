from jumpscale.data.serializers import json


class Serializer:
    def serialize(self, obj):
        return obj

    def deserialize(self, data):
        return data


class JsonSerializer(Serializer):
    def serialize(self, obj):
        return json.dumps(obj)

    def deserialize(self, data):
        return json.loads(data)
