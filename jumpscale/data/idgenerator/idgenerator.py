import random
import string
import uuid

def random_int(from_, to):
    return random.randint(from_, to)

def incrementor_id():
    # user redis.incr.
    raise NotImplementedError()

def guid():
    return str(uuid.uuid4())

def nfromchoices(n, choices):
    return "".join([random.choice(choices) for _ in range(n)])

def chars(nchars):
    choices = string.ascii_letters + string.digits
    return nfromchoices(nchars, choices)

def nbytes(nbytes):
    out = bytearray()
    for n in range(nbytes):
        out.append(random_int(0, 255))
    return out

def password(nchars):
    choices = string.printable
    return nfromchoices(nchars, choices)

def capnp_id():
    """
    Generates a valid id for a capnp schema.
    """
    # the bitwise is for validating the id check capnp/parser.c++
    return hex(random.randint(0, 2 ** 64) | 1 << 63)