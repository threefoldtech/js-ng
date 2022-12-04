import binascii
import nacl.utils

from nacl.public import PrivateKey, PublicKey, Box
from nacl.secret import SecretBox
from nacl.signing import SigningKey, VerifyKey
from nacl.exceptions import BadSignatureError


class NACL:
    KEY_SIZE = 32

    def __init__(self, private_key=None, symmetric_key=None):
        """Constructor for nacl object

        Args:
            private_key (bytes, optional): The private key used to sign and encrypt the data. Generated randomly if not given.
            symmetric_key (bytes, optional): The key used for symmetric encryption. Generated randomly if not given.
        """
        self.signing_key = SigningKey(private_key) if private_key else SigningKey.generate()
        self.verify_key = self.signing_key.verify_key
        self.private_key = self.signing_key.to_curve25519_private_key()
        self.public_key = self.private_key.public_key
        self.symmetric_key = nacl.utils.random(NACL.KEY_SIZE) if symmetric_key is None else symmetric_key
        self.symmetric_box = SecretBox(self.symmetric_key)

    def encrypt(self, message, reciever_public_key):
        """Encrypt the message to send to a receiver. (public key encryption)

        Args:
            message (bytes): The message to be encrypted.
            reciever_public_key (bytes): The receiver's public key.

        Returns:
            bytes: The encrypted message
        """
        return Box(self.private_key, PublicKey(reciever_public_key)).encrypt(message)

    def decrypt(self, message, sender_public_key):
        """Decrypt a received message. (public key encryption)

        Args:
            message (bytes): The encrypted message.
            sender_public_key (bytes): The public key of the sender.

        Returns:
            bytes: The decrypted message
        """
        return Box(self.private_key, PublicKey(sender_public_key)).decrypt(message)

    def encrypt_symmetric(self, message):
        """Encrypt the message to send to a receiver. (secret key encryption)

        Args:
            message (bytes): The message to be encrypted.

        Returns:
            bytes: The encrypted message
        """
        return self.symmetric_box.encrypt(message)

    def decrypt_symmetric(self, message, symmetric_key):
        """Decrypt the receiver message. (secret key encryption)

        Args:
            message (bytes): The message to be decrypted.

        Returns:
            bytes: The decrypted message
        """
        return SecretBox(symmetric_key).decrypt(message)

    def sign(self, message):
        """Sign the message and return the messsage and the signature.

        Args:
            message (bytes): The message to be signed

        Returns:
            bytes, bytes: The message and the signature.
        """
        signed = self.signing_key.sign(message)
        return message, signed.signature

    def sign_hex(self, message):
        """Sign the message and return the messsage and the signature.

        Args:
            message (bytes): The message to be signed

        Returns:
            bytes: The message and the signature.
        """
        signed = self.signing_key.sign(message)
        signedhex = binascii.hexlify(signed.signature)
        return signedhex

    def verify(self, message, signature, verification_key):
        """Verify that the signature using the verification key

        Args:
            message (bytes): The received message.
            signature (bytes): The recieved signature.
            verification_key (bytes): The verification key.

        Returns:
            bool: True if the verification succeeds.
        """
        try:
            VerifyKey(verification_key).verify(message, signature)
            return True
        except BadSignatureError:
            return False

    def get_signing_seed(self):
        """Returns the signing seed (same as the private key).

        Returns:
            bytes: The 32-bit signing key.
        """
        return bytes(self.signing_key._seed)

    def get_verification_key(self):
        """Returns the verification key.

        Returns:
            bytes: The verification key.
        """
        return bytes(self.verify_key)

    def get_verify_key_hex(self):
        return binascii.hexlify(self.verify_key.encode()).decode()

    def get_public_key_hex(self):
        return binascii.hexlify(self.public_key.encode()).decode()

    def get_public_key(self):
        """Getter for the public key.

        Returns:
            bytes: The public key.
        """
        return bytes(self.public_key)

    def get_private_key(self):
        """Getter for the private key.

        Returns:
            bytes: The private key.
        """
        return bytes(self.private_key)

    def get_symmetric_key(self):
        """Getter for the symmetric key.

        Returns:
            bytes: The symmetric key.
        """
        return bytes(self.symmetric_key)
