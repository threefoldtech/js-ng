import pytoml
from .dictionary import merge


def fancydumps(obj, secure=False):
    """fancydump dict object into toml stream 
    
    Arguments:
        obj (dict) : the dict which will be dumped     
    
    Returns:
        string : the toml stream
    """
    if not isinstance(obj, dict):
        raise Exception("need to be dict")

    keys = [item for item in obj.keys()]
    keys.sort()

    out = ""
    prefix = ""
    lastprefix = ""
    for key in keys:

        val = obj[key]
        if "." in key:
            prefix, key.split(".", 1)
        else:
            prefix = key[0:6]

        if prefix != lastprefix:
            out += "\n"
            lastprefix = prefix
        ttype = type(val)
        if secure and key.endswith("_") and ttype.BASETYPE == "string":
            # TODO
            "to do when Jumpscale/data/nacl/NACL.py is completed"

        out += "%s\n" % (ttype.toml_string_get(val, key=key))
    out = out.replace("\n\n\n", "\n\n")

    return out.strip()


def dumps(obj):
    """dump dict object into toml stream 
    
    Arguments:
        obj (dict) : the dict which will be dumped     
    
    Returns:
        string : the toml stream
    """
    return pytoml.dumps(obj, sort_keys=True)


def loads(s, secure=False):
    """loads the data from toml string into dict
    
    Arguments:
        s (string) : the toml stream
    
    Returns:
        dict : the loaded data from toml stram
    """
    if isinstance(s, bytes):
        s = s.decode("utf-8")
    try:
        val = pytoml.loads(s)
    except Exception as e:
        raise RuntimeError("Toml deserialization failed for:\n%s.\nMsg:%s" % (str(s), str(e)))
    if secure and isinstance(val, dict):
        # TODO
        "to do when Jumpscale/data/nacl/NACL.py is completed"
    return val


def merge_toml(
    tomlsource,
    tomlupdate,
    keys_replace={},
    add_non_exist=False,
    die=True,
    errors=[],
    listunique=False,
    listsort=True,
    liststrip=True,
):

    """the values of the tomlupdate will be applied on tomlsource (are strings or dicts)
    
    Arguments:
    add_non_exist : if False then will die if there is a value in the dictupdate which is not in the dictsource
    keys_replace : key = key to replace with value in the dictsource (which will be the result)
    

    Raises:
        RuntimeError : error
    
    Returns:
        dict,errors : if die=False then will return errors, the list has the keys which were in dictupdate but not in dictsource
        listsort means that items in list will be sorted (list at level 1 under dict)
    """
    if isinstance(tomlsource, str):
        try:
            dictsource = loads(tomlsource)
        except Exception:
            raise RuntimeError("toml file source is not properly formatted.")
    else:
        dictsource = tomlsource
    if isinstance(tomlupdate, str):
        try:
            dictupdate = loads(tomlupdate)
        except Exception:
            raise RuntimeError("toml file source is not properly formatted.")
    else:
        dictupdate = tomlupdate
    return merge(
        dictsource,
        dictupdate,
        keys_replace=keys_replace,
        add_non_exist=add_non_exist,
        die=die,
        errors=errors,
        listunique=listunique,
        listsort=listsort,
        liststrip=liststrip,
    )

