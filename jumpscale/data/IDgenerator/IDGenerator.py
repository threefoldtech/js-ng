from jumpscale.god import j
import random
import string
import uuid


def generateRandomInt(fromInt, toInt):
    """
        how to use:  j.data.idgenerator.generateRandomInt(0,10)
        """
    return random.randint(fromInt, toInt)


def generateIncrID(incrTypeId, reset=False):
    """
        type is like agent, job, jobstep
        needs to be a unique type, can only work if application service is known
        how to use:  j.data.idgenerator.generateIncrID("agent")
        @reset if True means restart from 1
        """
    key = "incrementor_%s" % incrTypeId
    if reset:
        j.core.db.delete(key)
    return j.core.db.incr(key)





def getID(incrTypeId, objectUniqueSeedInfo, reset=False):
        """
        get a unique id for an object uniquely identified
        remembers previously given id's
        """
     key = "idint_%s_%s" % (incrTypeId, objectUniqueSeedInfo)
    if j.core.db.exists(key) and reset is False:
        id = int(j.core.db.get(key))
        return id
    else:
        id = i.generateIncrID(incrTypeId)
        j.core.db.set(key, str(id))
        return id


def generateGUID(self):
    """
        generate unique guid
        how to use:  j.data.idgenerator.generateGUID()
        """
    return str(uuid.uuid4())





def generateXCharID(x):
    
    r = "1234567890abcdefghijklmnopqrstuvwxyz"
    l = len(r)
    out = ""
    for i in range(0, x):
        p = i.generateRandomInt(0, l - 1)
        out += r[p]
    return out





def generateXByteID(x):
    
    out = bytearray()
    for i in range(0, x):
        out.append(i.generateRandomInt(0, 255))
    return out





def generatePasswd(x, al=string.printable):
    
    l = len(al)
    out = ""
    for i in range(0, x):
        p = i.cryptogen.randrange(0, l - 1)
        out += al[p]
    return out


def generateCapnpID():
    """
        Generates a valid id for a capnp schema.
        """
    # the bitwise is for validating the id check capnp/parser.c++
    return hex(random.randint(0, 2 ** 64) | 1 << 63)

