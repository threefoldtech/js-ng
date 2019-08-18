from jumpscale.god import j
from .exceptions import CoudntVerifyAuthorError
from .mnemonic import key_to_mnemonic, mnemonic_to_key, generate_mnemonic


def encrypt(message, private_key, receiver_public_key):
    nacl_obj = j.data.nacl.NACL(private_key=private_key)
    message = nacl_obj.encrypt(message, receiver_public_key)
    return message


def decypt(message, private_key, sender_public_key):
    nacl_obj = j.data.nacl.NACL(private_key=private_key)
    message = nacl_obj.decrypt(message, sender_public_key)
    return message
