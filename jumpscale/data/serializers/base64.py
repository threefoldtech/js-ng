import base64


def encode(s):
    if isinstance(s,str):
        b = s.encode()
    else:
        b = s
    return base64.b64encode(b)

def dumps(s):
    return encode(s).decode()

def decode(b):
    if isinstance(b,str):
        b = b.encode()
    return base64.b64decode(b)

def loads(s):
    return decode(s).decode()