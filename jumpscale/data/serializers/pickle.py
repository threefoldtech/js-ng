import pickle


def dumps(obj):
    """dump dict object into pickle stream 
    
    Arguments:
        obj (dict) : the dict which will be dumped     
    
    Returns:
        string : the pickle stream
    """
    return pickle.dumps(obj)


def loads(s):
    """loads the data from pickle string into dict
    
    Arguments:
        s (string) : the pickle stream
    
    Returns:
        dict : the loaded data from pickle stram
    """
    return pickle.loads(s)
