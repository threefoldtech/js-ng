import yaml
import json
import toml


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
    elif type=='toml':
        return load_toml(string)
    else:
        raise Exception ('the type must be yaml,toml or')

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
    elif type=='toml':
        return dump_toml(dict)
    else:
        raise Exception ('the type must be yaml,toml or')

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

def load_toml(string):
    """convert toml string to dict
    
    Arguments:
        string {str} -- the toml string
    
    Returns:
        dict -- the converted dict
    """
    d=toml.loads(string)
    return d

def dump_toml(dict):
    """convert dict to toml string
    
    Arguments:
        dict {dict} -- the dict will be converted
    
    Returns:
        str -- the toml string generated from dict
    """
    s=toml.dumps(dict)
    return s
