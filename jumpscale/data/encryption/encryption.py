from jumpscale.data.nacl import NACL
from .mnemonic import key_to_mnemonic, mnemonic_to_key, generate_mnemonic


def encrypt(message, private_key, receiver_public_key):
    """Encrypt the message using the public key of the reciever and the sender's private key.

    Args:
        message (bytes): The message.
        private_key (bytes): sender's private key.
        receiver_public_key (bytes): receiver's public key.

    Returns:
        bytes: The encryption of the message.
    """
    nacl_obj = NACL(private_key=private_key)
    message = nacl_obj.encrypt(message, receiver_public_key)
    return message


def decrypt(message, private_key, sender_public_key):
    """Decrypt the message using the private key of the reciever and the sender's public key.

    Args:
        message (bytes): The message.
        private_key (bytes): reciever's private key.
        sender_public_key (bytes): sender's public key.

    Returns:
        bytes: The decryption of the message.
    """
    nacl_obj = NACL(private_key=private_key)
    message = nacl_obj.decrypt(message, sender_public_key)
    return message


def encrypt_symmetric(message, symmetric_key):
    """Encrypt the message using the secret key.

    Args:
        message (bytes): The message.
        symmetric_key (bytes): The secret key.

    Returns:
        bytes: The encryption of the message.
    """
    nacl_obj = NACL(symmetric_key=symmetric_key)
    return nacl_obj.encrypt_symmetric(message)


def decrypt_symmetric(message, symmetric_key):
    """Decrypt the message using the secret key.

    Args:
        message (bytes): The message.
        symmetric_key (bytes): The secret key.

    Returns:
        bytes: The decryption of the message.
    """
    nacl_obj = NACL(symmetric_key=symmetric_key)
    return nacl_obj.decrypt_symmetric(message, symmetric_key)
