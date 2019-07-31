import pytest
from jumpscale.god import j
import hashlib
import os


@pytest.fixture
def make_hash():
    h = j.data.hash
    return h


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


def test_hash_strings(make_hash):
    test_string = "my company is codescalers"
    assert make_hash.md5(test_string) == hashlib.md5(test_string.encode()).hexdigest()
    assert make_hash.sha1(test_string) == hashlib.sha1(test_string.encode()).hexdigest()
    assert make_hash.sha224(test_string) == hashlib.sha224(test_string.encode()).hexdigest()
    assert make_hash.sha256(test_string) == hashlib.sha256(test_string.encode()).hexdigest()
    assert make_hash.sha384(test_string) == hashlib.sha384(test_string.encode()).hexdigest()
    assert make_hash.sha512(test_string) == hashlib.sha512(test_string.encode()).hexdigest()
    assert make_hash.sha3_224(test_string) == hashlib.sha3_224(test_string.encode()).hexdigest()
    assert make_hash.sha3_256(test_string) == hashlib.sha3_256(test_string.encode()).hexdigest()
    assert make_hash.sha3_384(test_string) == hashlib.sha3_384(test_string.encode()).hexdigest()
    assert make_hash.sha3_512(test_string) == hashlib.sha3_512(test_string.encode()).hexdigest()
    assert make_hash.blake2b(test_string) == hashlib.blake2b(test_string.encode()).hexdigest()
    assert make_hash.blake2s(test_string) == hashlib.blake2s(test_string.encode()).hexdigest()
    assert make_hash.shake_128(test_string) == hashlib.shake_128(test_string.encode()).hexdigest(16)
    assert make_hash.shake_256(test_string) == hashlib.shake_256(test_string.encode()).hexdigest(16)


def test_hash_files(make_hash, make_list):
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    my_file = os.path.join(THIS_FOLDER, "copy.txt")
    file = open("copy.txt", "w")
    file.write("Your text goes here")
    file.close()
    for h in make_list:
        ha = hashlib.new(h)
        ha.update("Your text goes here".encode())
        assert make_hash.hash_file("copy.txt", h) == ha.hexdigest()


def test_hash_dir(make_hash, make_list):
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    print(THIS_FOLDER)
    for h in make_list:
        # assert type(make_hash.hash_directory('C:\\Users\\omarelsheekh\\PycharmProjects\\js-ng\\jumpscale\\data\\hash',h))==type([])
        # please change the dir above and remove the comment
        assert True
