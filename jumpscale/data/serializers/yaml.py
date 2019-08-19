import yaml


def dumps(obj):
    """dump dict object into yaml stream 
    
    Arguments:
        obj (dict) : the dict which will be dumped     
    
    Returns:
        string : the yaml stream
    """
    return yaml.dump(obj)


def loads(s):
    """loads the data from yaml string into dict
    
    Arguments:
        s (string) : the yaml stream
    
    Returns:
        dict : the loaded data from yaml stram
    """
    return yaml.load(s)

