import random
import string
import uuid


def random_int(from_, to):
    """Generate rondom int
   
   Arguments:
       from_ (int) : starting number
       to (int) :  ending number
   
   Returns:
       str : returns random number 
   """
    return random.randint(from_, to)


def incrementor_id():
    # user redis.incr.
    raise NotImplementedError()


def guid():
    """Generates a random ID from module UUID.
    
    Returns:
        str : returns unique ID 
    """
    return str(uuid.uuid4())


def n_from_choices(n, choices):
    """generate a string composed of n randomely chosen strings from choices
    
    Arguments:
        n (int) : number of choices. 
        choices (str) : list of chars.
    
    Returns:
        str : list of choices.
    """

    return "".join([random.choice(choices) for _ in range(n)])


def chars(nchars):
    """ Generate characters.
    
    Arguments:
        nchars (int) : Number of chars 
    
    Returns:
       str : string composed of letters and digits 
    """
    choices = string.ascii_letters + string.digits
    return n_from_choices(nchars, choices)


def n_bytes(nbytes):
    """ Generate Byte array 
    
    Arguments:
        nbytes (str) : length of byte array
    
    Returns:
        str : out 
    """
    out = bytearray()
    for _ in range(nbytes):
        out.append(random_int(0, 255))
    return out


def password(nchars):
    """ Generate Password.
    
    Arguments:
        nchars (int) : number of chars.
    
    Returns:
        str : n from choices
    """

    choices = string.printable
    return n_from_choices(nchars, choices)


def capnp_id():
    """ Generate capnp schema ID.
    
    Returns:
        str : random hex 
    """

    # the bitwise is for validating the id check capnp/parser.c++
    return hex(random.randint(0, 2 ** 64) | 1 << 63)
