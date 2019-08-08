import yaml
from collections import OrderedDict


def dumps(obj):
    """dump dict object into yaml stream 
    
    Arguments:
        obj (dict) : the dict which will be dumped     
    
    Returns:
        string : the yaml stream
    """
    return yaml.dump(obj, default_flow_style=False, default_style="", indent=4, line_break="\n")


def loads(s):
    """loads the data from yaml string into dict
    
    Arguments:
        s (string) : the yaml stream
    
    Returns:
        dict : the loaded data from yaml stram
    """
    return yaml.load(s,Loader=yaml.SafeLoader)


def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    """load a yaml stream and keep the order
    
    Arguments:
        stream (string) : the yaml stream
    
    Keyword Arguments:
        Loader (yaml loader) : the yaml loader (default: {yaml.Loader})
        object_pairs_hook (dict) : the object pairs hook (default: {OrderedDict})
    
    Returns:
        dict : the loaded dict
    """

    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)
    return yaml.load(stream, OrderedLoader)


def ordered_dump(data, stream=None, Dumper=yaml.Dumper, **kwds):
    """dump a yaml stream with keeping the order
    
    Arguments:
        data (dict) : the dict of data
    
    Keyword Arguments:
        stream () : the data stream (default: {None})
        Dumper (yaml.dumper) : the yaml dumper (default: {yaml.Dumper})
    
    Returns:
        string : the dumped yaml stream
    """

    class OrderedDumper(Dumper):
        pass

    def _dict_representer(dumper, data):
        return dumper.represent_mapping(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, data.items())

    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, **kwds)

