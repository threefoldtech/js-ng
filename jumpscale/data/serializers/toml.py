import pytoml


def dumps(d):
    """dump dict object into toml stream 
    
    Arguments:
        d (dict) : the dict which will be dumped     
    
    Returns:
        string : the toml stream
    """
    s = pytoml.dumps(d)
    return s


def loads(s):
    """loads the data from toml string into dict
    
    Arguments:
        s (string) : the toml stream
    
    Returns:
        dict : the loaded data from toml stram
    """
    d = pytoml.loads(s)
    return d

