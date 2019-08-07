import pytest
from jumpscale.god import j
import hashlib
import os


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
    assert j.data.hash.md5(test_string).hexdigest() == hashlib.md5(test_string.encode()).hexdigest()
    assert j.data.hash.sha1(test_string).hexdigest() == hashlib.sha1(test_string.encode()).hexdigest()
    assert j.data.hash.sha224(test_string).hexdigest() == hashlib.sha224(test_string.encode()).hexdigest()
    assert j.data.hash.sha256(test_string).hexdigest() == hashlib.sha256(test_string.encode()).hexdigest()
    assert j.data.hash.sha384(test_string).hexdigest() == hashlib.sha384(test_string.encode()).hexdigest()
    assert j.data.hash.sha512(test_string).hexdigest() == hashlib.sha512(test_string.encode()).hexdigest()
    assert j.data.hash.sha3_224(test_string).hexdigest() == hashlib.sha3_224(test_string.encode()).hexdigest()
    assert j.data.hash.sha3_256(test_string).hexdigest() == hashlib.sha3_256(test_string.encode()).hexdigest()
    assert j.data.hash.sha3_384(test_string).hexdigest() == hashlib.sha3_384(test_string.encode()).hexdigest()
    assert j.data.hash.sha3_512(test_string).hexdigest() == hashlib.sha3_512(test_string.encode()).hexdigest()
    assert j.data.hash.blake2b(test_string).hexdigest() == hashlib.blake2b(test_string.encode()).hexdigest()
    assert j.data.hash.blake2s(test_string).hexdigest() == hashlib.blake2s(test_string.encode()).hexdigest()
    assert j.data.hash.shake_128(test_string).hexdigest(16) == hashlib.shake_128(test_string.encode()).hexdigest(16)
    assert j.data.hash.shake_256(test_string).hexdigest(16) == hashlib.shake_256(test_string.encode()).hexdigest(16)

def test_hash_bytes():
    test_string = b'hi there'
    assert j.data.hash.md5(test_string).hexdigest() == hashlib.md5(test_string).hexdigest()
    assert j.data.hash.sha1(test_string).hexdigest() == hashlib.sha1(test_string).hexdigest()
    assert j.data.hash.sha224(test_string).hexdigest() == hashlib.sha224(test_string).hexdigest()
    assert j.data.hash.sha256(test_string).hexdigest() == hashlib.sha256(test_string).hexdigest()
    assert j.data.hash.sha384(test_string).hexdigest() == hashlib.sha384(test_string).hexdigest()
    assert j.data.hash.sha512(test_string).hexdigest() == hashlib.sha512(test_string).hexdigest()
    assert j.data.hash.sha3_224(test_string).hexdigest() == hashlib.sha3_224(test_string).hexdigest()
    assert j.data.hash.sha3_256(test_string).hexdigest() == hashlib.sha3_256(test_string).hexdigest()
    assert j.data.hash.sha3_384(test_string).hexdigest() == hashlib.sha3_384(test_string).hexdigest()
    assert j.data.hash.sha3_512(test_string).hexdigest() == hashlib.sha3_512(test_string).hexdigest()
    assert j.data.hash.blake2b(test_string).hexdigest() == hashlib.blake2b(test_string).hexdigest()
    assert j.data.hash.blake2s(test_string).hexdigest() == hashlib.blake2s(test_string).hexdigest()
    assert j.data.hash.shake_128(test_string).hexdigest(16) == hashlib.shake_128(test_string).hexdigest(16)
    assert j.data.hash.shake_256(test_string).hexdigest(16) == hashlib.shake_256(test_string).hexdigest(16)


def test_hash_files(make_list):
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    os.path.join(THIS_FOLDER, "copy.txt")
    file = open("copy.txt", "w")
    file.write("Your text goes here")
    file.close()
    for h in make_list:
        ha = hashlib.new(h)
        ha.update("Your text goes here".encode())
        assert j.data.hash.hash_file("copy.txt", h).hexdigest() == ha.hexdigest()
    os.remove('copy.txt')


def test_hash_dir(make_list):
    cdir=os.getcwd()
    os.mkdir(cdir+'/omar')
    os.path.join(cdir+'/omar','hi.txt')
    file = open(cdir+"/omar/hi.txt", "w")
    file.write("hi there")
    file.close()
    for h in make_list:
        ha = hashlib.new(h)
        ha.update("hi there".encode())
        assert j.data.hash.hash_directory(cdir+'/omar',h)[0].hexdigest() == ha.hexdigest()
    os.remove(cdir+'/omar/hi.txt')
    os.rmdir(cdir+'/omar')
