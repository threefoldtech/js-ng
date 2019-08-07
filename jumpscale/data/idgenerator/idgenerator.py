import random
import string
import uuid


def random_int(from_, to):
   """Generate rondom int
   
   Arguments:
       from_ {int} -- starting number
       to {int} --  ending number
   
   Returns:
       str -- returns random number 
   """
   return random.randint(from_, to)


def incrementor_id():
    # user redis.incr.
    raise NotImplementedError()


def guid():
    """Generates a random ID from module UUID.
    
    Returns:
        str -- returns unique ID 
    """
    return str(uuid.uuid4())


def n_from_choices(n, choices):
    """ 
    
    Arguments:
        n {[type]} -- [description]
        choices {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """

    return "".join([random.choice(choices) for _ in range(n)])

        
def chars(nchars):
    """[summary]
    
    Arguments:
        nchars {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    choices = string.ascii_letters + string.digits
    return n_from_choices(nchars, choices)


def n_bytes(nbytes):
    """[summary]
    
    Arguments:
        nbytes {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """

    out = bytearray()
    for _ in range(nbytes):
        out.append(random_int(0, 255))
    return out


def password(nchars):
    """[summary]
    
    Arguments:
        nchars {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
     

    choices = string.printable
    return n_from_choices(nchars, choices)


def capnp_id():
    """[summary]
    
    Returns:
        [type] -- [description]
    """

    # the bitwise is for validating the id check capnp/parser.c++
    return hex(random.randint(0, 2 ** 64) | 1 << 63)
    