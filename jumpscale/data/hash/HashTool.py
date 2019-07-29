import hashlib,os
MD5=0
SHA1=1
SHA224=2
SHA256=3
SHA384=4
SHA512=5
SHA3_224=6
SHA3_256=7
SHA3_384=8
SHA3_512=9
SHAKE_128=10
SHAKE256=11
BLAKE2B=12
BLAKE2S=13

def getListOfFiles(dirName):
    # create a list of file and sub directories
    # names in the given directory
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)

    return allFiles
def md5_str(string,encod='utf-8'):
    return hashlib.md5(string.encode(encod)).hexdigest()

def sha1_str(string,encod='utf-8'):
    return hashlib.sha1(string.encode(encod)).hexdigest()

def sha224_str(string,encod='utf-8'):
    return hashlib.sha224(string.encode(encod)).hexdigest()

def sha384_str(string,encod='utf-8'):
    return hashlib.sha384(string.encode(encod)).hexdigest()

def sha256_str(string,encod='utf-8'):
    return hashlib.sha256(string.encode(encod)).hexdigest()

def sha512_str(string,encod='utf-8'):
    return hashlib.sha512(string.encode(encod)).hexdigest()

def sha3_224_str(string,encod='utf-8'):
    return hashlib.sha3_224(string.encode(encod)).hexdigest()

def sha3_256_str(string,encod='utf-8'):
    return hashlib.sha3_256(string.encode(encod)).hexdigest()

def sha3_384_str(string,encod='utf-8'):
    return hashlib.sha3_384(string.encode(encod)).hexdigest()

def sha3_512_str(string,encod='utf-8'):
    return hashlib.sha3_512(string.encode(encod)).hexdigest()

def blake2s_str(string,encod='utf-8'):
    return hashlib.blake2s(string.encode(encod)).hexdigest()

def blake2b_str(string,encod='utf-8'):
    return hashlib.blake2b(string.encode(encod)).hexdigest()

def shake_128_str(string,encod='utf-8'):
    return hashlib.shake_128(string.encode(encod)).hexdigest(16)

def shake_256_str(string,encod='utf-8'):
    return hashlib.shake_256(string.encode(encod)).hexdigest(16)

def set_things(s,e):
    l=[md5_str(s,e),sha224_str(s,e),sha256_str(s,e),sha384_str(s,e),sha512_str(s,e)
       ,sha3_224_str(s,e),sha3_256_str(s,e),sha3_384_str(s,e),sha3_512_str(s,e),
       shake_128_str(s,e),shake_256_str(s,e),blake2b_str(s,e),blake2s_str(s,e)]
    return l

def hash_file(directory,hash_type):
    file = open(directory)
    fileStr = file.read()
    encode=file.encoding
    file.close()
    l=set_things(fileStr,encode)
    return l[hash_type]

def hash_directory(root_dir,hash_type):
    hashes_list=[]
    for d in getListOfFiles(root_dir):
        print(d)
        hashes_list.append(hash_file(d,hash_type))
    return hashes_list

if __name__ == '__main__':
    print(hash_file('../pdoc.txt', SHA1))
    print(hash_directory('test',MD5))