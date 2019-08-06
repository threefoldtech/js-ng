from blosc import compress, decompress


def dumps(obj):
    return compress(obj, typesize=8)


def loads(s):
    return decompress(s)
