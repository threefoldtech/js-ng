import yaml
import json


def load(string,type):
    """convert any formater to dict
    
    Arguments:
        string {str} -- the string must be converted
        type {str} -- the formater type
    
    Raises:
        Exception: will be raised if user enterd not listed type
    
    Returns:
        dict -- the converted dict 
    """
    if type=='yaml':
        return load_yaml(string)
    else:
        raise Exception ('the type must be yaml or...')

def dump(dict,type):
    """convert dict to formated string
    
    Arguments:
        dict {dict} -- the which will be converted
        type {str} -- the type of the formater
    
    Raises:
        Exception: will be raised if user enterd not listed type
    
    Returns:
        str -- the formated string
    """
    if type=='yaml':
        return dump_yaml(dict)
    else:
        raise Exception ('the type must be yaml or...')

def load_yaml(string):
    """convert yaml string to dict
    
    Arguments:
        string {str} -- the yaml string
    
    Returns:
        dict -- the converted dict
    """
    d=yaml.safe_load(string)
    return d

def dump_yaml(dict):
    """convert dict to yaml string
    
    Arguments:
        dict {dict} -- the dict will be converted
    
    Returns:
        str -- the yaml string generated from dict
    """
    y=yaml.safe_dump(dict)
    return y

