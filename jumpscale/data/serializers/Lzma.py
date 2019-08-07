import pylzma

def dumps(obj):
    return pylzma.compress(obj)

def loads(s):
    return pylzma.decompress(s)