import hashlib
import os


def get_list_files(dir_name):
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

def md5(string,encode='utf-8'):
    return hashlib.md5(string.encode(encode)).hexdigest()

def sha1(string,encode='utf-8'):
    return hashlib.sha1(string.encode(encode)).hexdigest()

def sha224(string,encode='utf-8'):
    return hashlib.sha224(string.encode(encode)).hexdigest()

def sha384(string,encode='utf-8'):
    return hashlib.sha384(string.encode(encode)).hexdigest()

def sha256(string,encode='utf-8'):
    return hashlib.sha256(string.encode(encode)).hexdigest()

def sha512(string,encode='utf-8'):
    return hashlib.sha512(string.encode(encode)).hexdigest()

def sha3_224(string,encode='utf-8'):
    return hashlib.sha3_224(string.encode(encode)).hexdigest()

def sha3_256(string,encode='utf-8'):
    return hashlib.sha3_256(string.encode(encode)).hexdigest()

def sha3_384(string,encode='utf-8'):
    return hashlib.sha3_384(string.encode(encode)).hexdigest()

def sha3_512(string,encode='utf-8'):
    return hashlib.sha3_512(string.encode(encode)).hexdigest()

def blake2s(string,encode='utf-8'):
    return hashlib.blake2s(string.encode(encode)).hexdigest()

def blake2b(string,encode='utf-8'):
    return hashlib.blake2b(string.encode(encode)).hexdigest()

def shake_128(string,encode='utf-8'):
    return hashlib.shake_128(string.encode(encode)).hexdigest(16)

def shake_256(string,encode='utf-8'):
    return hashlib.shake_256(string.encode(encode)).hexdigest(16)

hash_types={'md5':md5,'sha1':sha1,'sha224':sha224,'sha256':shake_256,'sha384':sha384,'sha512':sha512,
            'sha3_224':sha3_224,'sha3_256':sha3_256,'sha3_384':sha3_384,'sha3_512':sha3_512,
            'blake2s':blake2s,'black2b':blake2b,'shake_128':shake_128,'shake_256':shake_256}

def hash_file(directory,hash_type):
    f = open(directory)
    fileStr =f.read()
    encode=f.encoding
    f.close()
    return hash_types[hash_type](fileStr,encode)

def hash_directory(root_dir,hash_type):
    hashes_list=[]
    for d in get_list_files(root_dir):
        hashes_list.append(hash_file(d,hash_type))
    return hashes_list
