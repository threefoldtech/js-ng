import snappy


def dumps(obj):
    return snappy.compress(obj)


def loads(s):
    return snappy.decompress(s)
