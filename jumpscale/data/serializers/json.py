import json


class Encoder(object):
    @staticmethod
    def get(encoding="ascii"):
        kls = json.JSONEncoder
        kls.ENCODING = encoding
        return kls


def dumps(self, obj, sort_keys=False, indent=False, encoding="ascii"):
    return json.dumps(obj, ensure_ascii=False, sort_keys=sort_keys, indent=indent, cls=Encoder.get(encoding=encoding))


def loads(self, s):
    if isinstance(s, bytes):
        s = s.decode("utf-8")
    return json.loads(s)
