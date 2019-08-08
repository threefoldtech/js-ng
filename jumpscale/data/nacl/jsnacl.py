import nacl.utils

from nacl.public import PrivateKey, PublicKey, Box
from nacl.secret import SecretBox
from nacl.signing import SigningKey, VerifyKey


class NACL:
    KEY_SIZE = 32

    def __init__(self, private_key=None, symmetric_key=None, signing_seed=None):
        self.private_key = PrivateKey.generate() if private_key is None else PrivateKey(private_key)
        self.public_key = self.private_key.public_key
        self.symmetric_key = nacl.utils.random(KEY_SIZE) if symmetric_key is None else symmetric_key
        self.signing_key = SigningKey.generate() if signing_seed is None else SigningKey(signing_seed)
        self.symmetric_box = SecretBox(self.symmetric_key)

    def encrypt(self, message, reciever_public_key):
        return Box(self.private_key, PublicKey(reciever_public_key)).encrypt(message)

    def decrypt(self, message, sender_public_key):
        return Box(self.private_key, PublicKey(sender_public_key)).decode(message)

    def encrypt_symmetric(self, message):
        return self.symmetric_box.encrypt(message)

    def sign(self, message):
        return self.signing_key.sign(message)

    def verify(self, message, signature, verification_key):
        return VerifyKey(verification_key).verify(message, signature)

    def get_signing_seed(self):
        return bytes(self.signing_key._seed)

    def get_verification_key(self):
        return bytes(self.signing_key.verify_key)

    def get_public_key(self):
        return bytes(self.public_key)

    def get_private_key(self):
        return bytes(self.private_key)

    def get_symmetric_key(self):
        return bytes(self.symmetric_key)
