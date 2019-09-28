import pathlib
import tempfile
import os
import shutil
import stat
from distutils import dir_util
from typing import List

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


def home():
    return str(pathlib.Path.home())


def cwd():
    """Return current working directory.

    Returns:
        str: current directory.
    """
    return str(pathlib.Path.cwd())


def is_dir(path: str) -> bool:
    """Checks if path is a dir

    :param path: path to check
    :type path: str
    :return: True if is dir else False
    :rtype: bool
    """
    return pathlib.Path(path).is_dir()


def is_file(path: str) -> bool:
    """Checks if path is a file

    :param path: path to check
    :type path: str
    :return: True if is file else False
    :rtype: bool
    """
    return pathlib.Path(path).is_file()


def is_symlink(path: str) -> bool:
    """Checks if path symlink

    Args:
        path (str): path to check if symlink

    Returns:
        bool: True if symlink False otherwise
    """
    return pathlib.Path(path).is_symlink()


def is_absolute(path: str) -> bool:
    """Checks if path is absolute

    Returns:
        bool: True if absolute
    """
    return pathlib.Path(path).is_absolute()


def is_mount(path: str) -> bool:
    """Checks if path is mount

    Returns:
        bool: True if mount
    """
    return pathlib.Path(path).is_mount()


def is_ascii_file(path: str, checksize=4096) -> bool:
    """Checks if file `path` is ascii

    Args:
        path (str): file path
        checksize (int, optional): checksize. Defaults to 4096.

    Returns:
        bool: True if ascii file
    """
    # TODO: let's talk about checksize feature.
    try:
        with open(path, encoding="ascii") as f:
            f.read()
            return True
    except UnicodeDecodeError:
        return False


def is_empty_dir(path: str) -> bool:
    """Checks if path is emptry directory

    Args:
        path (str): path to check if empty directory

    Returns:
        bool: True if path is emptry directory
    """

    try:
        g = pathlib.Path(path).iterdir()
        next(g)
    except StopIteration:
        # means we can't get next entry -> dir is empty.
        return True
    else:
        return False


is_binary_file = lambda path: not is_ascii_file(path)


def is_broken_link(path: str, clean=False) -> bool:
    """Checks if path is a broken symlink

    Args:
        path (str): path to check
        clean (bool, optional): remove symlink if broken. Defaults to False.

    Raises:
        NotImplementedError: [description]

    Returns:
        bool: True if path is a broken symlink
    """
    raise NotImplementedError()


def stem(path: str) -> str:
    """returns the stem of a path (path without parent directory and without extension)
    e.g
        In [2]: t = j.sals.fs.stem("/tmp/tmp-5383p1GOmMOOwvfi.tpl")

        In [3]: t
        Out[3]: 'tmp-5383p1GOmMOOwvfi'

    Args:
        path (str): path we want to get its stem

    Returns:
        [type]: [description]
    """
    return pathlib.Path(path).stem


def mkdir(path: str, exist_ok=True):
    """Makes directory at path

    Args:
        path (str): path to create dir at
        exist_ok (bool, optional): won't fail if directory exists. Defaults to True.

    Returns:
        [type]: [description]
    """
    return pathlib.Path(path).mkdir(exist_ok=exist_ok)


def mkdirs(path: str, exist_ok=True):
    """Creates dir as well as all non exisitng parents in the path

    Args:
        path (str): path to create dir at
        exist_ok (bool, optional): won't fail if directory exists. Defaults to True.
    """
    return os.makedirs(path, exist_ok=exist_ok)


def parent(path: str) -> str:
    """Get path's parent

    Args:
        path (str): path to get its parent

    Returns:
        str: parent path.
    """
    return str(pathlib.Path(path).parent)


def parents(path: str) -> List[str]:
    """Get parents list

    e.g
    >>> j.sals.fs.parents("/tmp/home/ahmed/myfile.py")
    [PosixPath('/tmp/home/ahmed'),
    PosixPath('/tmp/home'),
    PosixPath('/tmp'),
    PosixPath('/')]

    Args:
        path (str): path to get its parents

    Returns:
        List[str]: list of parents
    """

    return list([str(p) for p in pathlib.Path(path).parents])


def path_parts(path: str) -> List[str]:
    """Convert path to a list of parts
    e.g
     '/tmp/tmp-5383p1GOmMOOwvfi.tpl' ->  ('/', 'tmp', 'tmp-5383p1GOmMOOwvfi.tpl')
    Args:
        path (str): path to convert to parts

    Returns:
        List[str]: path parts.
    """
    return pathlib.Path(path).parts


def exists(path: str) -> bool:
    """Checks if path exists

    Args:
        path (str): path to check for existence

    Returns:
        bool: True if exists
    """
    return pathlib.Path(path).exists()


def rename(path1: str, path2: str):
    """Rename path1 to path2

    Args:
        path1 (str): source path
        path2 (str): dest path

    """
    return pathlib.Path(path1).rename(path2)


def expanduser(path: str) -> str:
    """Expands the tilde `~` to username
    e.g
        j.sals.fs.expanduser("~/work") -> '/home/xmonader/work'
    Args:
        path (str): path with optionally `~`

    Returns:
        str: path with tilde `~` resolved.
    """
    return str(pathlib.Path(path).expanduser())


def unlink(path: str):
    """unlink path

    Args:
        path (str): path to unlink


    """
    return pathlib.Path(path).unlink()


def read_text(path: str) -> str:
    """read ascii content at `path`

    Args:
        path (str): ascii file path

    Returns:
        str: ascii content in path
    """
    return pathlib.Path(path).read_text()


read_ascii = read_file = read_text


def read_bytes(path: str) -> bytes:
    """read binary content at `path`

    Args:
        path (str): binary file path

    Returns:
        bytes: binary content in path
    """
    return pathlib.Path(path).read_bytes()


read_binary = read_file_binary = read_bytes


def write_text(path: str, data: str, encoding=None):
    """write text `data` to path `path` with encoding

    Args:
        path (str): path to write to
        data (str): ascii content
        encoding ([type], optional): encoding. Defaults to None.


    """
    return pathlib.Path(path).write_text(data, encoding)


write_ascii = write_file = write_text


def write_bytes(path: str, data: bytes):
    """write binary `data` to path `path`

    Args:
        path (str): path to write to
        data (bytes): binary content

    """
    return pathlib.Path(path).write_bytes(data)


write_binary = write_file_binary = write_bytes


def touch(path: str):
    """create file

    Args:
        path (str): path to create file

    """
    return pathlib.Path(path).touch()


def get_temp_filename(mode="w+b", buffering=-1, encoding=None, newline=None, suffix=None, prefix=None, dir=None) -> str:
    """Get temp filename

    Args:
        mode (str, optional): [description]. Defaults to "w+b".
        buffering (int, optional): buffering. Defaults to -1.
        encoding ([type], optional): encoding . Defaults to None.
        newline ([type], optional):  Defaults to None.
        suffix ([type], optional): ending suffix. Defaults to None.
        prefix ([type], optional): prefix . Defaults to None.
        dir ([type], optional): where to create the file. Defaults to None.

    Returns:
        [str]: temp filename
    """
    return tempfile.NamedTemporaryFile(mode, buffering, encoding, newline, suffix, prefix, dir).name


def get_temp_dirname(suffix=None, prefix=None, dir=None) -> str:
    """Get temp directory name

    Args:
        suffix ([type], optional): ending suffix. Defaults to None.
        prefix ([type], optional): prefix . Defaults to None.
        dir ([type], optional): where to create the directory. Defaults to None.


    Returns:
        str: temp directory name.
    """
    return tempfile.TemporaryDirectory(suffix, prefix, dir).name


NamedTemporaryFile = tempfile.NamedTemporaryFile
TempraryDirectory = tempfile.TemporaryDirectory
mkdtemp = tempfile.mkdtemp
mkstemp = tempfile.mkstemp
get_temp_dir = tempfile.gettempdir


def parts_to_path(parts: List[str]) -> str:
    """Convert list of path parts into a path string

    Args:
        parts (List[str]): path parts

    Returns:
        str: joined path parts
    """
    path = pathlib.Path(parts[0])
    for p in parts[1:]:
        path = path.joinpath(p)
    return str(path)


def join_paths(*paths):
    return parts_to_path(paths)


def rm_emptry_dir(path: str):
    """Remove empty directory

    Args:
        path (str): path to remove.
    """
    path = pathlib.Path(path)
    path.rmdir()


def rmtree(path: str):
    """Remove directory tree
    Args:
        path (str): path to remove
    """
    path = pathlib.Path(path)
    if path.is_file() or path.is_symlink():
        os.remove(path)
    elif path.is_dir():
        shutil.rmtree(path)


def copy_stat(src: str, dst: str, times=True, perms=True):
    """Copy stat of src to dst

    Args:
        src (str): source path
        dst (str): destination
        times (bool, optional):  Defaults to True.
        perms (bool, optional): permissions Defaults to True.
    """
    st = os.stat(src)
    if hasattr(os, "utime"):
        os.utime(dst, (st.st_atime, st.st_mtime))
    if hasattr(os, "chmod"):
        m = stat.S_IMODE(st.st_mode)
        os.chmod(dst, m)


def copy_file(src: str, dst: str, times=False, perms=False):
    """Copy the file, optionally copying the permission bits (mode) and
        last access/modify time. If the destination file exists, it will be
        replaced. Raises OSError if the destination is a directory. If the
        platform does not have the ability to set the permission or times,
        ignore it.
        This is shutil.copyfile plus bits of shutil.copymode and
        shutil.copystat's implementation.
        shutil.copy and shutil.copy2 are not supported but are easy to do.

    Args:
        src (str): source path
        dst (str): destination

    """
    shutil.copyfile(src, dst)
    if times or perms:
        copy_stat(src, dst, times, perms)


copy_tree = dir_util.copy_tree
chdir = os.chdir


def change_dir(path: str) -> str:
    """Change current working directory to `path`

    Args:
        path (str): path to switch current working directory to

    Returns:
        str: new current working dir
    """
    os.chdir(path)
    return path


def chmod(path: str, mode):
    """change file mode for path to mode

    Args:
        path (str): path
        mode (int): file mode

    """
    return pathlib.Path(path).chmod(mode)


def lchmod(path: str, mode):
    """change file mode for path to mode (handles links too)

    Args:
        path (str): path
        mode (int): file mode

    """
    return pathlib.Path(path).lchmod(mode)


def stat(path: str):
    """Gets stat of path `path`

    Args:
        path (str): path to get its stat

    Returns:
        stat_result: returns stat struct.
    """

    return pathlib.Path(path).stat()


def lstat(path: str):
    """Gets stat of path `path` (handles links)

    Args:
        path (str): path to get its stat

    Returns:
        stat_result: returns stat struct.
    """

    return pathlib.Path(path).lstat()


def resolve(path: str) -> str:
    """resolve `.` and `..` in path

    Args:
        path (str): path with optionally `.` and `..`

    Returns:
        str: resolved path
    """
    return pathlib.Path(path).resolve()


def extension(path: str, include_dot=True):
    """Gets the extension of path
    '/home/ahmed/myfile.py' -> `.py` if include_dot else `py`

    Args:
        path (str): [description]
        include_dot (bool, optional): controls whether to include the dot or not. Defaults to True.

    Returns:
        str: extension
    """
    splitted = os.path.splitext(path)
    ext = ""
    if len(splitted) == 1:
        return ext

    if include_dot:
        return splitted[1]
    else:
        return splitted[1].strip(".")


ext = extension


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


def walk(path: str, pat="*", filter_fun=default_filter_fun):
    """walk recursively on path
    e.g
        for el in walk('/tmp', filter_fun=j.sals.fs.is_file) : ..
        for el in walk('/tmp', filter_fun=j.sals.fs.is_dir) : ..
        for el in walk('/tmp', filter_fun= lambda x: len(x)>4 and (j.sals.fs.is_file(x) or j.sals.fs.is_dir(x)) ) : ..


    Args:
        path (str): path to walk over
        pat (str, optional): pattern to match against. Defaults to "*".
        filter_fun (Function, optional): filtering function. Defaults to default_filter_fun which accepts anything.
    """
    p = pathlib.Path(path)
    for entry in p.rglob(pat):
        # use rglob instead of glob("**/*")
        if filter_fun(entry):
            yield str(entry )


def walk_non_recursive(path: str, filter_fun=default_filter_fun):
    """walks non recursively on path
    e.g
        for el in walk('/tmp', filter=j.sals.fs.is_file) : ..
        for el in walk('/tmp', filter=j.sals.fs.is_dir) : ..
        for el in walk('/tmp', filter= lambda x: len(x)>4 and (j.sals.fs.is_file(x) or j.sals.fs.is_dir(x)) ) : ..


    Args:
        path (str): path to walk over
        pat (str, optional): pattern to match against. Defaults to "*".
        filter_fun (Function, optional): filtering function. Defaults to default_filter_fun which accepts anything.
    """
    p = pathlib.Path(path)
    for entry in p.iterdir():
        if filter_fun(entry):
            yield str(entry)


def walk_files(path: str, recursive=True):
    """
    walk over files in path and applies function `fun`
    e.g

        for el in walk_files('/tmp') : ..

    Args:
        path (str): path to walk over
        recursive (bool, optional): recursive or not. Defaults to True.


    """

    if recursive:
        return walk(path, filter_fun=is_file)
    else:
        return walk_non_recursive(path, filter_fun=is_file)


def walk_dirs(path, recursive=True):
    """
        walk over directories in path and applies function `fun`
    e.g

        for el in walk_dirs('/tmp') : ..


    Args:
        path (str): path to walk over
        recursive (bool, optional): recursive or not. Defaults to True.


    """
    if recursive:
        return walk(path, filter_fun=is_dir)
    else:
        return walk_non_recursive(path, filter_fun=is_dir)
