# coding: utf-8
import hashlib
import pytest
import os
import tempfile

from jumpscale.loader import j


@pytest.fixture
def make_list():
    hashes_list = [
        "md5",
        "sha1",
        "sha224",
        "sha256",
        "sha384",
        "sha512",
        "sha3_224",
        "sha3_256",
        "sha3_384",
        "sha3_512",
        "blake2s",
        "blake2b",
    ]
    return hashes_list


def test_hash_strings():
    test_string = "my company is codescalers"
    assert j.data.hash.md5(test_string) == hashlib.md5(test_string.encode()).hexdigest()
    assert j.data.hash.sha1(test_string) == hashlib.sha1(test_string.encode()).hexdigest()
    assert j.data.hash.sha224(test_string) == hashlib.sha224(test_string.encode()).hexdigest()
    assert j.data.hash.sha256(test_string) == hashlib.sha256(test_string.encode()).hexdigest()
    assert j.data.hash.sha384(test_string) == hashlib.sha384(test_string.encode()).hexdigest()
    assert j.data.hash.sha512(test_string) == hashlib.sha512(test_string.encode()).hexdigest()
    assert j.data.hash.sha3_224(test_string) == hashlib.sha3_224(test_string.encode()).hexdigest()
    assert j.data.hash.sha3_256(test_string) == hashlib.sha3_256(test_string.encode()).hexdigest()
    assert j.data.hash.sha3_384(test_string) == hashlib.sha3_384(test_string.encode()).hexdigest()
    assert j.data.hash.sha3_512(test_string) == hashlib.sha3_512(test_string.encode()).hexdigest()
    assert j.data.hash.blake2b(test_string) == hashlib.blake2b(test_string.encode()).hexdigest()
    assert j.data.hash.blake2s(test_string) == hashlib.blake2s(test_string.encode()).hexdigest()
    assert j.data.hash.shake_128(test_string) == hashlib.shake_128(test_string.encode()).hexdigest(16)
    assert j.data.hash.shake_256(test_string) == hashlib.shake_256(test_string.encode()).hexdigest(16)


def test_hash_bytes():
    test_string = b"hi there"
    assert j.data.hash.md5(test_string) == hashlib.md5(test_string).hexdigest()
    assert j.data.hash.sha1(test_string) == hashlib.sha1(test_string).hexdigest()
    assert j.data.hash.sha224(test_string) == hashlib.sha224(test_string).hexdigest()
    assert j.data.hash.sha256(test_string) == hashlib.sha256(test_string).hexdigest()
    assert j.data.hash.sha384(test_string) == hashlib.sha384(test_string).hexdigest()
    assert j.data.hash.sha512(test_string) == hashlib.sha512(test_string).hexdigest()
    assert j.data.hash.sha3_224(test_string) == hashlib.sha3_224(test_string).hexdigest()
    assert j.data.hash.sha3_256(test_string) == hashlib.sha3_256(test_string).hexdigest()
    assert j.data.hash.sha3_384(test_string) == hashlib.sha3_384(test_string).hexdigest()
    assert j.data.hash.sha3_512(test_string) == hashlib.sha3_512(test_string).hexdigest()
    assert j.data.hash.blake2b(test_string) == hashlib.blake2b(test_string).hexdigest()
    assert j.data.hash.blake2s(test_string) == hashlib.blake2s(test_string).hexdigest()
    assert j.data.hash.shake_128(test_string) == hashlib.shake_128(test_string).hexdigest(16)
    assert j.data.hash.shake_256(test_string) == hashlib.shake_256(test_string).hexdigest(16)


def test_hash_files(make_list):
    with tempfile.NamedTemporaryFile("w") as tf:
        tf.write("Your text goes here")
        tf.flush()
        for h in make_list:
            ha = hashlib.new(h)
            ha.update("Your text goes here".encode(tf.encoding))
            assert j.data.hash.hash_file(tf.name, h).hexdigest() == ha.hexdigest()


def test_hash_dir(make_list):
    dir_path = tempfile.mkdtemp()
    with tempfile.NamedTemporaryFile("w", dir=dir_path) as tf:
        tf.write("عربى english")
        tf.flush()

    for h in make_list:
        ha = hashlib.new(h)
        ha.update("عربى english".encode())
        base_hexdigest = ha.hexdigest()
        for value in j.data.hash.hash_directory(dir_path, h).values():
            assert value == base_hexdigest
