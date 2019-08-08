import snappy


def compress(obj):
    """compress string with snappy algorithm
    
    Arguments:
        obj (string) : the string will be encoded
    
    Returns:
        bytes : the compressed bytes
    """
    return snappy.compress(obj)


def decompress(s):
    """decompress snappy bytes to original obj
    
    Arguments:
        s (bytes) : the bytes will be compressed
    
    Returns:
        (string) : the decompressed string
    """
    return snappy.decompress(s)
