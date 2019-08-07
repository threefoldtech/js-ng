import blosc


def compress(obj):
    return blosc.compress(obj, typesize=8)


def decompress(s):
    return blosc.decompress(s)
