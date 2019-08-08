import msgpack


def dumps(obj):
    """dump dict object into msgpack stream 
    
    Arguments:
        obj (dict) : the dict which will be dumped     
    
    Returns:
        string : the msgpack stream
    """
    return msgpack.packb(obj, use_bin_type=True)


def loads(s):
    """loads the data from msgpack string into dict
    
    Arguments:
        s (string) : the msgpack stream
    
    Returns:
        dict : the loaded data from msgpack stram
    """
    if isinstance(s, (bytes, bytearray)):
        return msgpack.unpackb(s, raw=False)
    return False
