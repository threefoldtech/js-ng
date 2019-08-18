import os
import hashlib

from .exceptions import FailedChecksumError


wordlist = []
with open("wordlist.txt", "r") as f:
    wordlist = [line.strip() for line in f.readlines()]


def generate_mnemonic(strength=256, wordlist=wordlist):
    ent = entropy(strength)
    return key_to_mnemonic(ent)


def entropy(strength=256, wordlist=wordlist):
    assert strength >= 128 and strength <= 256 and strength % 32 == 0
    return os.urandom(strength // 8)


def mnemonic_to_key(mnemonic, wordlist=wordlist):
    words = mnemonic.split(" ")
    indexes = list(map(_word_index, words))
    total_length = len(indexes) * 11
    strength = total_length * 32 // 33
    checksum_length = total_length - strength
    binary_string = to_bin(indexes, 11)
    data = binary_string[0:strength]
    decrypted = bytes([int(data[i : i + 8], 2) for i in range(0, len(data), 8)])
    if not _verify_checksum(decrypted, binary_string[strength:]):
        raise FailedChecksumError("The received package is corrupt.")
    return decrypted


def _verify_checksum(data, checksum):
    sha256_hash = hashlib.sha256(data).hexdigest().encode()
    return to_bin(sha256_hash)[0 : len(data) * 8 // 32] == checksum


def _word_index(word, wordlist=wordlist):
    lo, hi = 0, len(wordlist) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if word <= wordlist[mid]:
            hi = mid
        else:
            lo = mid + 1
    return lo


def key_to_mnemonic(key, wordlist=wordlist):
    sha256_hash = hashlib.sha256(key).hexdigest().encode()
    strength = len(key) * 8
    checksum_length = strength // 32
    total_length = strength + checksum_length
    binary_string = (to_bin(key) + to_bin(sha256_hash)[0:checksum_length])[0:total_length]
    sentence = ""
    assert total_length % 11 == 0
    for i in range(total_length // 11):
        sentence += " " + wordlist[int(binary_string[i * 11 : (i + 1) * 11], 2)]
    return sentence[1:]


def to_bin(arr, bytelen=8):
    result = ""
    for c in arr:
        result += ("0" * bytelen + bin(c)[2:])[-bytelen:]
    return result
