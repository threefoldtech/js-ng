import yaml
import json
import toml
import base64


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
    elif type=='json':
        return load_json(string)
    elif type=='base64':
        return load_base64(string)
    else:
        raise Exception ('the type must be yaml,toml,json, or base64')

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
    elif type=='json':
        return dump_json(dict)
    elif type=='base64':
        return dump_base64(dict)
    else:
        raise Exception ('the type must be yaml,toml,dict, or base')

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

def load_json(string):
    """convert json string to dict
    
    Arguments:
        string {str} -- the json string
    
    Returns:
        dict -- the converted dict
    """
    d=json.loads(string.replace('\'','\"'))
    return d

def dump_json(dict):
    """convert dict to json string
    
    Arguments:
        dict {dict} -- the dict will be converted
    
    Returns:
        str -- the json string generated from dict
    """
    s=json.dumps(dict)
    return s

def load_base64(data):
    """convert base string or bytes to dict
    
    Arguments:
        data {str or dict} -- the base64 string or bytes
    
    Returns:
        dict -- the converted dict
    """
    d={}
    if isinstance(data,bytes):
        d={'bytes':data,'string':base64.decodebytes(data)}
    else:
        d={'bytes':base64.encodebytes(data.encode()),'string':data}
    return d

def dump_base64(dict):
    """convert dict to base64 bytes
    
    Arguments:
        dict {dict} -- the dict will be converted
    
    Returns:
        byte -- the json bytes in dict
    """
    return dict['bytes']

