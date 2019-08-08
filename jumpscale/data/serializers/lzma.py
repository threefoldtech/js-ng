import pylzma

def compress(obj):
    """compress string with lzma algorithm
    
    Arguments:
        obj (string) : the string will be encoded
    
    Returns:
        bytes : the compressed bytes
    """
    return pylzma.compress(obj)

def decompress(s):
    """decompress lzma bytes to original obj
    
    Arguments:
        s (bytes) : the bytes will be compressed
    
    Returns:
        (string) : the decompressed string
    """
    return pylzma.decompress(s)