import nacl.utils

from nacl.public import PrivateKey, PublicKey, Box
from nacl.secret import SecretBox
from nacl.signing import SigningKey, VerifyKey

KEY_SIZE = 32


def generate_random_key(size=KEY_SIZE):
    return nacl.utils.random(size)


def asymmetric_box(private_key, public_key):
    return Box(PrivateKey(private_key), PublicKey(public_key))


def public_from_private(private_key):
    return bytes(PrivateKey(private_key).public_key)


def verifaction_from_signing(seed):
    return bytes(SigningKey(seed).verify_key)


def symmetric_box(key):
    return SecretBox(key)


def encrypt_asymmetric(message, box):
    return box.encrypt(message)


def decrypt_asymmetric(message, box):
    return box.decrypt(message)


def encrypt_symmetric(message, box):
    return box.encrypt(message)


def decrypt_symmetric(message, box):
    return box.decrypt(message)


def sign(message, seed):
    signing_key = SigningKey(seed)
    signed = signing_key.sign(message)
    return signed.message, signed.signature


def verify(message, signature, verifaction_key):
    return VerifyKey(verifaction_key).verify(message, signature)
