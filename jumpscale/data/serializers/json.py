import json


def dumps(obj):
    """dump dict object into json stream

    Arguments:
        obj (dict) : the dict which will be dumped

    Returns:
        string : the json stream
    """
    return json.dumps(obj)


def dump_to_file(file_path, obj):
    """Writes the dumped obj to a file

   Args:
       file_path (str): path to write to
       obj (dict): the dict which will be dumped
   """
    with open(file_path, "w") as fp:
        json.dump(obj, fp)


def loads(s):
    """loads the data from json string into dict

    Arguments:
        s (string) : the json stream

    Returns:
        dict : the loaded data from json stram
    """
    if isinstance(s, bytes):
        s = s.decode("utf-8")
    return json.loads(s)


def load_from_file(file_path):
    """Loads data from file to a dict

    Args:
        file_path (str): path of the json file
    """
    with open(file_path) as fp:
        obj = json.load(fp)
    return obj
