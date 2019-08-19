import blosc


def compress(obj):
    """compress string with blosc algorithm
    
    Arguments:
        obj (string) : the string will be encoded
    
    Returns:
        bytes : the compressed bytes
    """
    return blosc.compress(obj)


def decompress(s):
    """decompress blosc bytes to original obj
    
    Arguments:
        s (bytes) : the bytes will be compressed
    
    Returns:
        (string) : the decompressed string
    """
    return blosc.decompress(s)
