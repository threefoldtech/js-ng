import pathlib
import tempfile
import os
import shutil
import stat
from distutils import dir_util

def home():
    return str(pathlib.Path.home())


def cwd():
    return str(pathlib.Path.cwd())


basename = os.path.basename
dirname = os.path.dirname
common_path = os.path.commonpath
common_prefix = os.path.commonprefix
norm_path = os.path.normpath
norm_case = os.path.normcase
get_access_time = os.path.getatime
get_modified_time = os.path.getmtime
get_creation_time = os.path.getctime
sep = os.path.sep
is_samefile = os.path.samefile
expandvars = os.path.expandvars
expanduser = os.path.expanduser

def is_dir(path):
    return pathlib.Path(path).is_dir()

def is_file(path):
    return pathlib.Path(path).is_file()


def is_symlink(path):
    return pathlib.Path(path).is_symlink()


def is_absolute(path):
    return pathlib.Path(path).is_absolute()


def is_mount(path):
    return pathlib.Path(path).is_mount()


def is_ascii_file(filename, checksize=4096):
    # TODO: let's talk about checksize feature.
    try:
        with open(filename, encoding="ascii") as f:
            f.read()
            return True
    except UnicodeDecodeError:
        return False


def is_empty_dir(path):
    try:
        g = pathlib.Path(path).iterdir()
        next(g)
    except StopIteration:
        # means we can't get next entry -> dir is empty.
        return True
    else:
        return False


is_binary_file = lambda path: not is_ascii_file(path)


def is_broken_link(path, clean=False):
    raise NotImplementedError()


def stem(path):
    return pathlib.Path(path).stem


def mkdir(path, exist_ok=True):
    return pathlib.Path(path).mkdir(exist_ok=exist_ok)


def parent(path):
    return pathlib.Path(path).parent


def parents(path):
    """
    [PosixPath('/tmp/home/ahmed'),
    PosixPath('/tmp/home'),
    PosixPath('/tmp'),
    PosixPath('/')]
    """
    return list(pathlib.Path(path).parnets)


def path_parts(path):
    return pathlib.Path(path).parts


def exists(path):
    return pathlib.Path(path).exists()


def rename(path1, path2):
    return pathlib.Path(path1).rename(path2)


def expanduser(path):
    return pathlib.Path(path).expanduser()


def unlink(path):
    return pathlib.Path(path).unlink()


def read_text(path):
    return pathlib.Path(path).read_text()


read_ascii = read_file = read_text


def read_bytes(path):
    return pathlib.Path(path).read_bytes()


read_binary = read_file_binary = read_bytes


def write_text(path, data, encoding=None):
    return pathlib.Path(path).write_text(data, encoding)


write_ascii = write_file = write_text


def write_bytes(path, data):
    return pathlib.Path(path).write_bytes(data)

write_binary = write_file_binary = write_bytes

def touch(path):
    return pathlib.Path(path).touch()


def get_temp_filename(mode="w+b", buffering=-1, encoding=None, newline=None, suffix=None, prefix=None, dir=None):
    return tempfile.NamedTemporaryFile(mode, buffering, encoding, newline, suffix, prefix, dir).name


def get_temp_dirname(suffix=None, prefix=None, dir=None):
    return tempfile.TemporaryDirectory(suffix, prefix, dir).name


NamedTemporaryFile = tempfile.NamedTemporaryFile
TempraryDirectory = tempfile.TemporaryDirectory
mkdtemp = tempfile.mkdtemp
mkstemp = tempfile.mkstemp
get_temp_dir = tempfile.gettempdir

def parts_to_path(parts):
    path = pathlib.Path(parts[0])
    for p in parts[1:]:
        path.joinpath(p)
    return path


def rm_emptry_dir(path):
    path = pathlib.Path(path)
    path.rmdir()


def rmtree(path):
    path = pathlib.Path(path)
    if path.is_file() or path.is_link():
        os.remove(path)
    elif path.is_dir():
        shutil.rmtree(path)
    if not parents:
        return
    p = path.parent
    while p:
        try:
            os.rmdir(p)
        except os.error:
            break
        p = p.parent


def copy_stat(src, dst, times=True, perms=True):
    st = os.stat(src)
    if hasattr(os, 'utime'):
        os.utime(dst, (st.st_atime, st.st_mtime))
    if hasattr(os, 'chmod'):
        m = stat.S_IMODE(st.st_mode)
        os.chmod(dst, m)

def copy_file(src, dst, times=False, perms=False):
    """Copy the file, optionally copying the permission bits (mode) and
        last access/modify time. If the destination file exists, it will be
        replaced. Raises OSError if the destination is a directory. If the
        platform does not have the ability to set the permission or times,
        ignore it.
        This is shutil.copyfile plus bits of shutil.copymode and
        shutil.copystat's implementation.
        shutil.copy and shutil.copy2 are not supported but are easy to do.
    """
    shutil.copyfile(src, dst)
    if times or perms:
        copy_stat(src, dst, times, perms)

def copy_stat(src, dst, times=True, perms=True):
    st = os.stat(src)
    if hasattr(os, 'utime'):
        os.utime(dst, (st.st_atime, st.st_mtime))
    if hasattr(os, 'chmod'):
        m = stat.S_IMODE(st.st_mode)
        os.chmod(dst, m)

copy_tree = dir_util.copy_tree
chdir = os.chdir

def change_dir(to):
    os.chdir(path)
    return cwd()


def chmod(path, mode):
    return pathlib.Path(path).chmod(mode)

def lchmod(path, mode):
    return pathlib.Path(path).lchmod(mode)


def stat(path):
    return pathlib.Path(path).stat()


def lstat(path):
    return pathlib.Path(path).lstat()


def resolve(path):
    return pathlib.Path(path).resolve()


def extension(path, include_dot=True):
    splitted = os.path.splitext(path)
    ext = ""
    if len(splitted) == 1:
        return ext

    if include_dot:
        return splitted[1]
    else:
        return splitted[1].strip(".")

def chown():
    raise NotImplementedError()

def read_link(path):
    raise NotImplementedError()

def remove_links(path):
    raise NotImplementedError()


def change_filenames(from_, to, where):
    pass

def replace_words_in_files(from_, to, where):
    pass

move = shutil.move


def default_filter_fun(entry):
    return True

def walk(path, fun, pat="*", filter_fun=default_filter_fun):
    p = pathlib.Path(path)
    for entry in p.rglob(pat):
        # use rglob instead of glob("**/*")
        if filter_fun(entry):
            fun(entry)


# walk_files('/tmp', lambda x: print(x.upper()), filter=j.sals.fs.is_file)
# walk_files('/tmp', lambda x: print(x.upper()), filter=j.sals.fs.is_dir)
# walk_files('/tmp', lambda x: print(x.upper()), filter= lambda x: len(x)>4 and (j.sals.fs.is_file(x) or j.sals.fs.is_dir(x)) )


def walk_non_recursive(path, fun, filter_fun=default_filter_fun):
    p = pathlib.Path(path)
    for entry in p.iterdir():
        if filter_fun(entry):
            fun(entry)

def walk_files(path, fun, recursive=True):
    if recursive:
        return walk(path, fun, filter_fun=is_file)
    else:
        return walk_non_recursive(path, fun, filter_fun=is_file)

def walk_dirs(path, fun, recursive=True):
    if recursive:
        return walk(path, fun, filter_fun=is_dir)
    else:
        return walk_non_recursive(path, fun, filter_fun=is_dir)

