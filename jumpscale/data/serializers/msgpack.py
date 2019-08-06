import msgpack


def dumps(obj):
    return msgpack.packb(obj, use_bin_type=True)


def loads(s):
    if isinstance(s, (bytes, bytearray)):
        return msgpack.unpackb(s, raw=False)
    return False
