import json


class Encoder(object):
    @staticmethod
    def get(encoding="ascii"):
        kls = json.JSONEncoder
        kls.ENCODING = encoding
        return kls


def dumps(obj, sort_keys=False, indent=False, encoding="ascii"):
    """dump dict object into json stream 
    
    Arguments:
        obj (dict) : the dict which will be dumped     
    
    Returns:
        string : the json stream
    """
    return json.dumps(obj, ensure_ascii=False, sort_keys=sort_keys, indent=indent, cls=Encoder.get(encoding=encoding))


def loads(s):
    """loads the data from json string into dict
    
    Arguments:
        s (string) : the json stream
    
    Returns:
        dict : the loaded data from json stram
    """
    if isinstance(s, bytes):
        s = s.decode("utf-8")
    return json.loads(s)
