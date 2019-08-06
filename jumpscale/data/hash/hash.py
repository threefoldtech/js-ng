import hashlib
import os


def get_list_files(dir_name):
    """[returns a list of directories for all files in a root folder]
    
    Arguments:
        dir_name {[str]} -- [the directory of the root folder]
    
    Returns:
        all_files {[list]} -- [the list of directories for all files in the root folder]
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
    """[create a md5 hash string for any string ]
    
    Arguments:
        string {[str]} -- [the string need to be hashed]
    
    Keyword Arguments:
        encode {str} -- [the encoding for the string] (default: {"utf-8"})
    
    Returns:
        [byte] -- [the hash bytes]
    """
    if isinstance(string, str):
        return hashlib.md5(string.encode(encode))
    return hashlib.md5(string)


def sha1(string, encode="utf-8"):
    """[create a sha1 hash string for any string ]
    
    Arguments:
        string {[str]} -- [the string need to be hashed]
    
    Keyword Arguments:
        encode {str} -- [the encoding for the string] (default: {"utf-8"})
    
    Returns:
        [byte] -- [the hash bytes]
    """
    if isinstance(string, str):
        return hashlib.sha1(string.encode(encode))
    return hashlib.sha1(string)


def sha224(string, encode="utf-8"):
    """[create a sha224 hash string for any string ]
    
    Arguments:
        string {[str]} -- [the string need to be hashed]
    
    Keyword Arguments:
        encode {str} -- [the encoding for the string] (default: {"utf-8"})
    
    Returns:
        [byte] -- [the hash bytes]
    """
    if isinstance(string, str):
        return hashlib.sha224(string.encode(encode))
    return hashlib.sha224(string)


def sha384(string, encode="utf-8"):
    """[create a sha384 hash string for any string ]
    
    Arguments:
        string {[str]} -- [the string need to be hashed]
    
    Keyword Arguments:
        encode {str} -- [the encoding for the string] (default: {"utf-8"})
    
    Returns:
        [byte] -- [the hash bytes]
    """
    if isinstance(string, str):
        return hashlib.sha384(string.encode(encode))
    return hashlib.sha384(string)


def sha256(string, encode="utf-8"):
    """[create a sha256 hash string for any string ]
    
    Arguments:
        string {[str]} -- [the string need to be hashed]
    
    Keyword Arguments:
        encode {str} -- [the encoding for the string] (default: {"utf-8"})
    
    Returns:
        [byte] -- [the hash bytes]
    """
    if isinstance(string, str):
        return hashlib.sha256(string.encode(encode))
    return hashlib.sha256(string)


def sha512(string, encode="utf-8"):
    """[create a sha512 hash string for any string ]
    
    Arguments:
        string {[str]} -- [the string need to be hashed]
    
    Keyword Arguments:
        encode {str} -- [the encoding for the string] (default: {"utf-8"})
    
    Returns:
        [byte] -- [the hash bytes]
    """
    if isinstance(string, str):
        return hashlib.sha512(string.encode(encode))
    return hashlib.sha512(string)


def sha3_224(string, encode="utf-8"):
    """[create a sha3_224 hash string for any string ]
    
    Arguments:
        string {[str]} -- [the string need to be hashed]
    
    Keyword Arguments:
        encode {str} -- [the encoding for the string] (default: {"utf-8"})
    
    Returns:
        [byte] -- [the hash bytes]
    """
    if isinstance(string, str):
        return hashlib.sha3_224(string.encode(encode))
    return hashlib.sha3_224(string)


def sha3_256(string, encode="utf-8"):
    """[create a sha3_256 hash string for any string ]
    
    Arguments:
        string {[str]} -- [the string need to be hashed]
    
    Keyword Arguments:
        encode {str} -- [the encoding for the string] (default: {"utf-8"})
    
    Returns:
        [byte] -- [the hash bytes]
    """
    if isinstance(string, str):
        return hashlib.sha3_256(string.encode(encode))
    return hashlib.sha3_256(string)


def sha3_384(string, encode="utf-8"):
    """[create a sha3_384 hash string for any string ]
    
    Arguments:
        string {[str]} -- [the string need to be hashed]
    
    Keyword Arguments:
        encode {str} -- [the encoding for the string] (default: {"utf-8"})
    
    Returns:
        [byte] -- [the hash bytes]
    """
    if isinstance(string, str):
        return hashlib.sha3_384(string.encode(encode))
    return hashlib.sha3_384(string)


def sha3_512(string, encode="utf-8"):
    """[create a sha3_512 hash string for any string ]
    
    Arguments:
        string {[str]} -- [the string need to be hashed]
    
    Keyword Arguments:
        encode {str} -- [the encoding for the string] (default: {"utf-8"})
    
    Returns:
        [byte] -- [the hash bytes]
    """
    if isinstance(string, str):
        return hashlib.sha3_512(string.encode(encode))
    return hashlib.sha3_512(string)


def blake2s(string, encode="utf-8"):
    """[create a blake2s hash string for any string ]
    
    Arguments:
        string {[str]} -- [the string need to be hashed]
    
    Keyword Arguments:
        encode {str} -- [the encoding for the string] (default: {"utf-8"})
    
    Returns:
        [byte] -- [the hash bytes]
    """
    if isinstance(string, str):
        return hashlib.blake2s(string.encode(encode))
    return hashlib.blake2s(string)


def blake2b(string, encode="utf-8"):
    """[create a blake2b hash string for any string ]
    
    Arguments:
        string {[str]} -- [the string need to be hashed]
    
    Keyword Arguments:
        encode {str} -- [the encoding for the string] (default: {"utf-8"})
    
    Returns:
        [byte] -- [the hash bytes]
    """
    if isinstance(string, str):
        return hashlib.blake2b(string.encode(encode))
    return hashlib.blake2b(string)


def shake_128(string, encode="utf-8"):
    """[create a shake_128 hash string for any string ]
    
    Arguments:
        string {[str]} -- [the string need to be hashed]
    
    Keyword Arguments:
        encode {str} -- [the encoding for the string] (default: {"utf-8"})
    
    Returns:
        [byte] -- [the hash bytes]
    """
    if isinstance(string, str):
        return hashlib.shake_128(string.encode(encode))
    return hashlib.shake_128(string)


def shake_256(string, encode="utf-8"):
    """[create a shake_256 hash string for any string ]
    
    Arguments:
        string {[str]} -- [the string need to be hashed]
    
    Keyword Arguments:
        encode {str} -- [the encoding for the string] (default: {"utf-8"})
    
    Returns:
        [byte] -- [the hash bytes]
    """
    if isinstance(string, str):
        return hashlib.shake_256(string.encode(encode))
    return hashlib.shake_256(string)


def hash_file(directory, hash_type):
    """[create hash string for a file]
    
    Arguments:
        directory {str} -- [the dir for the file]
        hash_type {str} -- [the type of the hash]
    
    Returns:
        [byte] -- [the hash bytes]
    """
    f = open(directory)
    h = hashlib.new(hash_type)
    while True:
        data = f.read(2 ** 20)
        if not data:
            break
        data = data.encode(f.encoding)
        h.update(data)
    f.close()
    return h


def hash_directory(root_dir, hash_type):
    """[create hash string list for the files in a folder]
    
    Arguments:
        root_dir {str} -- [the dir for the root folder]
        hash_type {str} -- [the type of the hash]
    
    Returns:
        [list] -- [the hashes list]
    """
    hashes_list = []
    for d in get_list_files(root_dir):
        hashes_list.append(hash_file(d, hash_type))
    return hashes_list

print(md5('hi').hexdigest()==hashlib.md5(b'hi').hexdigest())
print(md5(b'hi'))