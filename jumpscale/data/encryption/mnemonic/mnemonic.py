import os
import hashlib
import hmac
from pbkdf2 import PBKDF2

PBKDF2_ROUNDS = 2048


class Mnemonic:
    wordlist = []

    @classmethod
    def init_wordlist(cls):
        with open("wordlist.txt", "r") as f:
            cls.wordlist = [line.strip() for line in f.readlines()]

    @classmethod
    def generate_mnemonic(cls, strength=128):
        if cls.wordlist == []:
            cls.init_wordlist()
        ent = cls.entropy(strength)
        sha256_hash = hashlib.sha256(ent)
        checksum_length = strength / 32
        total_length = strength + checksum_length
        binary_string = (cls.to_bin(ent) + cls.to_bin(sha256_hash))[0:total_length]
        sentence = ""
        for i in range(total_length / 11):
            sentence += " " + cls.wordlist[int(binary_string[i * 11 : (i + 1 * 11)], 2)]
        return sentence[1:]

    @classmethod
    def entropy(cls, strength=128):
        assert strength >= 128 and strength <= 256 and strength % 32 == 0
        return os.urandom(strength // 8)

    @classmethod
    def mnemonic_to_seed(cls, mnemonic):
        return PBKDF2(mnemonic, "mnemonic", iterations=PBKDF2_ROUNDS, macmodule=hmac, digestmodule=hashlib.sha512).read(
            64
        )

    @classmethod
    def to_bin(cls, string):
        result = ""
        for c in string:
            result += bin(ord(c))[2:]
        return result
