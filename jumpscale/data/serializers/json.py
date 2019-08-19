import json


def dumps(obj):
    """dump dict object into json stream 
    
    Arguments:
        obj (dict) : the dict which will be dumped     
    
    Returns:
        string : the json stream
    """
    return json.dumps(obj)


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
