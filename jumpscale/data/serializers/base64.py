import base64


def encode(s):
    """encode string with base64 algorithm

    Arguments:
        s (string) : the string will be encoded

    Returns:
        bytes : the encoded bytes
    """
    if isinstance(s, str):
        b = s.encode()
    else:
        b = s
    return base64.b64encode(b)


def decode(b):
    """decode base64 bytes to original obj

    Arguments:
        b (bytes) : the bytes will be decoded

    Returns:
         (string) : the decoded string
    """
    if isinstance(b, str):
        b = b.encode()
    return base64.b64decode(b)
