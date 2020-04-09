"""idgenerator module helps with generating ids, guids, integers, chars, passwords, capnp id, a choice of a sequence

```
JS-NG> j.data.idgenerator.guid()                                                                    
'c1d14970-f17f-49a3-aa85-f722013ee448'

JS-NG> j.data.idgenerator.password(5)                                                               
'b6~Sl'

JS-NG> j.data.idgenerator.capnp_id()                                                                
'0xa414b890b73d0940'

JS-NG> j.data.idgenerator.random_int()                                                              
7

JS-NG> j.data.idgenerator.random_int(0, 5)                                                          
2
```
"""
import random
import string
import uuid
from typing import List


def random_int(from_: int = 0, to: int = 10) -> int:
    """Generate random int within range from_, to

    Arguments:
        from_ {int} -- lower limit, default 0
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
