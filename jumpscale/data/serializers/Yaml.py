from collections import OrderedDict
from yaml import load, load_all,Loader, dump, dump_all,resolver,Dumper,SafeLoader


def dumps(obj):
    return dump(obj, default_flow_style=False, default_style="", indent=4, line_break="\n")


def loads(s):
    return load(s,Loader=SafeLoader)


def ordered_load(stream, Loader=Loader, object_pairs_hook=OrderedDict):
    """
    load a yaml stream and keep the order
    """

    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)
    return load(stream, OrderedLoader)


def ordered_dump(data, stream=None, Dumper=Dumper, **kwds):
    """
    dump a yaml stream with keeping the order
    """

    class OrderedDumper(Dumper):
        pass

    def _dict_representer(dumper, data):
        return dumper.represent_mapping(resolver.BaseResolver.DEFAULT_MAPPING_TAG, data.items())

    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return dump(data, stream, OrderedDumper, **kwds)

