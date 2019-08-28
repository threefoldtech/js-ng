import pickle


def decompress(obj):
    """dump pickle bytes object into string 
    
    Arguments:
        obj (pickle bytes) : the pickle bytes which will be dumped     
    
    Returns:
        string : the string
    """
    return pickle.loads(obj)


def compress(obj):
    """loads the data from pickle string into pickle bytes
    
    Arguments:
        obj (string) : the string
    
    Returns:
        pickle bytes : the loaded data from pickle stram
    """
    return pickle.dumps(obj)
