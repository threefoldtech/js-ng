"""This module helps with everything related to hashing strings, bytes with popular algorithms like, md5, sha256, sha384, sha512, blake2

```
JS-NG> j.data.hash.md5("abc")                                                                       
'900150983cd24fb0d6963f7d28e17f72'

JS-NG> j.data.hash.sha1("abc")                                                                      
'a9993e364706816aba3e25717850c26c9cd0d89d'

JS-NG> j.data.hash.sha224("abc")                                                                    
'23097d223405d8228642a477bda255b32aadbce4bda0b3f7e36c9da7'

JS-NG> j.data.hash.sha512("abc")                                                                    
'ddaf35a193617abacc417349ae20413112e6fa4e89a97ea20a9eeee64b55d39a2192992a274fc1a836ba3c23a3feebbd454
d4423643ce80e2a9ac94fa54ca49f'

JS-NG> j.data.hash.blake2s("abc")                                                                   
'508c5e8c327c14e2e1a72ba34eeb452f37458b209ed63a294d999b4c86675982'

JS-NG>
```  
"""

import hashlib
import os


def encode_string(obj, encode):
    if isinstance(obj, str):
        return obj.encode(encode)
    return obj


def get_list_files(dir_name):
    """returns a list of directories for all files in a root folder

    Arguments:
        dir_name (str) : the directory of the root folder

    Returns:
        all_files (list) : the list of directories for all files in the root folder
    """
    # create a list of file and sub directories
    # names in the given directory
    files_list = os.listdir(dir_name)
    all_files = list()
    # Iterate over all the entries
    for entry in files_list:
        # Create full path
        full_path = os.path.join(dir_name, entry)
        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(full_path):
            all_files = all_files + get_list_files(full_path)
        else:
            all_files.append(full_path)

    return all_files


def md5(string, encode="utf-8"):
    """create a md5 hash string for any string

    Arguments:
        string (str): the string need to be hashed

    Keyword Arguments:
        encode (str): the encoding for the string (default: {"utf-8"})

    Returns:
        list of byte: the hash bytes
    """
    return hashlib.md5(encode_string(string, encode)).hexdigest()


def sha1(string, encode="utf-8"):
    """create a sha1 hash string for any string

    Arguments:
        string (str): the string need to be hashed

    Keyword Arguments:
        encode (str): the encoding for the string (default: {"utf-8"})

    Returns:
        list of byte: the hash bytes
    """
    return hashlib.sha1(encode_string(string, encode)).hexdigest()


def sha224(string, encode="utf-8"):
    """create a sha224 hash string for any string

    Arguments:
        string (str): the string need to be hashed

    Keyword Arguments:
        encode (str): the encoding for the string (default: {"utf-8"})

    Returns:
        list of byte: the hash bytes
    """
    return hashlib.sha224(encode_string(string, encode)).hexdigest()


def sha384(string, encode="utf-8"):
    """create a sha384 hash string for any string

    Arguments:
        string (str): the string need to be hashed

    Keyword Arguments:
        encode (str): the encoding for the string (default: {"utf-8"})

    Returns:
        list of byte: the hash bytes
    """
    return hashlib.sha384(encode_string(string, encode)).hexdigest()


def sha256(string, encode="utf-8"):
    """create a sha256 hash string for any string

    Arguments:
        string (str): the string need to be hashed

    Keyword Arguments:
        encode (str): the encoding for the string (default: {"utf-8"})

    Returns:
        list of byte: the hash bytes
    """
    return hashlib.sha256(encode_string(string, encode)).hexdigest()


def sha512(string, encode="utf-8"):
    """create a sha512 hash string for any string

    Arguments:
        string (str): the string need to be hashed

    Keyword Arguments:
        encode (str): the encoding for the string (default: {"utf-8"})

    Returns:
        list of byte: the hash bytes
    """
    return hashlib.sha512(encode_string(string, encode)).hexdigest()


def sha3_224(string, encode="utf-8"):
    """create a sha3_224 hash string for any string

    Arguments:
        string (str): the string need to be hashed

    Keyword Arguments:
        encode (str): the encoding for the string (default: {"utf-8"})

    Returns:
        list of byte: the hash bytes
    """
    return hashlib.sha3_224(encode_string(string, encode)).hexdigest()


def sha3_256(string, encode="utf-8"):
    """create a sha3_256 hash string for any string

    Arguments:
        string (str): the string need to be hashed

    Keyword Arguments:
        encode (str): the encoding for the string (default: {"utf-8"})

    Returns:
        list of byte: the hash bytes
    """
    return hashlib.sha3_256(encode_string(string, encode)).hexdigest()


def sha3_384(string, encode="utf-8"):
    """create a sha3_384 hash string for any string

    Arguments:
        string (str): the string need to be hashed

    Keyword Arguments:
        encode (str): the encoding for the string (default: {"utf-8"})

    Returns:
        list of byte: the hash bytes
    """
    return hashlib.sha3_384(encode_string(string, encode)).hexdigest()


def sha3_512(string, encode="utf-8"):
    """create a sha3_512 hash string for any string

    Arguments:
        string (str): the string need to be hashed

    Keyword Arguments:
        encode (str): the encoding for the string (default: {"utf-8"})

    Returns:
        list of byte: the hash bytes
    """
    return hashlib.sha3_512(encode_string(string, encode)).hexdigest()


def blake2s(string, encode="utf-8"):
    """create a blake2s hash string for any string

    Arguments:
        string (str): the string need to be hashed

    Keyword Arguments:
        encode (str): the encoding for the string (default: {"utf-8"})

    Returns:
        list of byte: the hash bytes
    """
    return hashlib.blake2s(encode_string(string, encode)).hexdigest()


def blake2b(string, encode="utf-8"):
    """create a blake2b hash string for any string

    Arguments:
        string (str): the string need to be hashed

    Keyword Arguments:
        encode (str): the encoding for the string (default: {"utf-8"})

    Returns:
        list of byte: the hash bytes
    """
    return hashlib.blake2b(encode_string(string, encode)).hexdigest()


def shake_128(string, encode="utf-8"):
    """create a shake_128 hash string for any string

    Arguments:
        string (str): the string need to be hashed

    Keyword Arguments:
        encode (str): the encoding for the string (default: {"utf-8"})

    Returns:
        list of byte: the hash bytes
    """
    return hashlib.shake_128(encode_string(string, encode)).hexdigest(16)


def shake_256(string, encode="utf-8"):
    """create a shake_256 hash string for any string

    Arguments:
        string (str): the string need to be hashed

    Keyword Arguments:
        encode (str): the encoding for the string (default: {"utf-8"})

    Returns:
        list of byte: the hash bytes
    """
    return hashlib.shake_256(encode_string(string, encode)).hexdigest(16)


# TODO: review
def hash_alg(name, data, **kwargs):
    """create a hash object

    Arguments:
        name (str) : name of algorithm name
        data (str) : data need to be hashed

    Returns:
        list of byte : the hash bytes
    """
    return hashlib.new(name, data, **kwargs)


def hash_file(path, hash_type):
    """create hash string for a file

    Arguments:
        path (str) : the path for the file
        hash_type (str) : the type of the hash

    Returns:
        list of byte : the hash bytes
    """
    with open(path, "rb") as f:
        h = hashlib.new(hash_type)
        while True:
            data = f.read(2 ** 20)
            if not data:
                break
            h.update(data)
        return h


# TODO: review and allow ignore files e.g .swp, .. etc
def hash_directory(root_dir, hash_type):
    """create hash string list for the files in a folder

    Arguments:
        root_dir (str) : the dir for the root folder
        hash_type (str) : the type of the hash

    Returns:
        dict : the hashes dict, keys are full paths and values are hexdigests
    """
    hashes = {}
    for d in get_list_files(root_dir):
        hashes[d] = hash_file(d, hash_type).hexdigest()
    return hashes
