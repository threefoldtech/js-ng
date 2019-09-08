import random
import string
import uuid
from typing import List


def random_int(from_: int, to: int) -> int:
    """Generate random int within range from_, to

    Arguments:
        from_ {int} -- lower limit
        to {int} -- upper limit

    Returns:
        int -- random number
    """
    return random.randint(from_, to)


def incrementor_id():
    # user redis.incr.
    raise NotImplementedError()


def guid() -> str:
    """Gets a uuid4

    Returns:
        str -- uuid4
    """
    return str(uuid.uuid4())


def nfromchoices(n: int, choices: List[str]) -> str:
    """Gets string from choices list

    Arguments:
        n {int} -- how many
        choices {List[str]} -- choices to pick from

    Returns:
        str -- joined result of n choices.
    """
    return "".join([random.choice(choices) for _ in range(n)])


def chars(nchars: int) -> str:
    """Gets a random string with length of n

    Arguments:
        nchars {int} -- [description]

    Returns:
        str -- [description]
    """
    choices = string.ascii_letters + string.digits
    return nfromchoices(nchars, choices)


def nbytes(nbytes: int) -> bytearray:
    """return bytearray of length n

    Arguments:
        nbytes {int} -- number of bytes to generate

    Returns:
        bytearray -- result
    """
    out = bytearray()
    for n in range(nbytes):
        out.append(random_int(0, 255))
    return out


def password(nchars: int) -> str:
    """Return a password of length nchars

    Arguments:
        nchars {int} -- [description]

    Returns:
        str -- password
    """
    choices = string.printable
    return nfromchoices(nchars, choices)


def capnp_id() -> str:
    """
    Generates a valid id for a capnp schema.

    Returns:
        str -- capnp id
    """
    # the bitwise is for validating the id check capnp/parser.c++
    return hex(random.randint(0, 2 ** 64) | 1 << 63)
