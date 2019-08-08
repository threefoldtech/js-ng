from jumpscale.god import j
from .exceptions import CoudntVerifyAuthorError


def sign_encrypt(message, private_key, receiver_public_key):
    nacl_obj = j.data.nacl.NACL(private_key=private_key, signing_seed=private_key)
    message, signature = nacl_obj.sign(message)
    message = nacl_obj.encrypt(message, receiver_public_key)
    signature = nacl_obj.encrypt(signature, receiver_public_key)
    return message, signature


def decypt_verify(message, signature, private_key, sender_public_key, verification_key):
    nacl_obj = j.data.nacl.NACL(private_key=private_key, signing_seed=private_key)
    message = nacl_obj.decrypt(message, sender_public_key)
    signature = nacl_obj.decrypt(signature, sender_public_key)
    if not nacl_obj.verify(message, signature, verification_key):
        raise CoudntVerifyAuthorError("The sender of the message couldn't be verified")
    return message
