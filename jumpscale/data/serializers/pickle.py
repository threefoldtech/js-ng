from pickle import dumps, loads


def decompress(obj):
    """convert back (loads) pickle bytes into an python object hierarchy 
    
    Arguments:
        obj (pickle bytes) : the pickle bytes which will be unpickling     
    
    Returns:
        object : the reconstituted python object hierarchy
    """
    return loads(obj)


def compress(obj):
    """convert (dumps) a Python object hierarchy into a byte stream
    
    Arguments:
        obj (object) : an python object hierarchy
    
    Returns:
        bytes-like object : the pickled representation of the object
    """
    return dumps(obj)
