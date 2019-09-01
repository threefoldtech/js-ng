import sys
import re
import os
import hashlib
import fnmatch
import inspect  # needed for getPathOfRunningFunction
import shutil
import tempfile
import codecs
import pickle as pickle
import stat
from stat import ST_MTIME
import stat
from functools import wraps
import copy
from jumpscale.god import j


def copy_file(filefrom, to, create_dir_ifneeded=False, overwritefile=True):
    """ Copy File.

    Args:
        fileFrom (str): Source file path name.
        to (str):  Destination file or folder path name.
        create_dir_ifneeded (bool): Defaults to False.
        overwritefile (bool):  Defaults to True.
        """
    # Create target folder first, otherwise copy fails
    target_folder = os.path.dirname(to)
    if create_dir_ifneeded:
        create_dir(target_folder)
    if exists(to):
        if os.path.samefile(filefrom, to):
            raise RuntimeError("{src} and {dest} are the same file".format(src=filefrom, dest=to))
        if overwritefile is False:
            if os.path.samefile(to, target_folder):
                destfilename = os.path.join(to, os.path.basename(filefrom))
                if exists(destfilename):
                    return
            else:
                return
        elif is_file(to):
            # overwriting some open  files is frustrating and may not work
            # due to locking [delete/copy is a better strategy]
            remove(to)
    shutil.copy(filefrom, to)


def move_file(source, destin):
    """ Move a  File from source path to destination path.

    Args:
        source (str): Source File Path.
        destin (str): Destination Path The File Should Be Moved to.
    """
    _move(source, destin)


def rename_file(filepath, new_name):
    """ Rename File.

    Args:
        filepath (str): Path of the file.
        new_name (str): New name of the file.

    Returns:
        str: File path + New name
    """
    return _move(filepath, new_name)


def remove_irrelevant_files(path, followsymlinks=True):
    """ Will remove files having extensions: pyc, bak.

    Args:
        path (str): path to search in.
        followsymlinks (bool): Defaults to True.
    """
    ext = ["pyc", "bak"]
    for path in list_files_in_dir(path, recursive=True, followsymlinks=followsymlinks):
        if get_file_extension(path) in ext:
            remove(path)


def remove(path):
    """ Remove a File.

    Args:
        path (str): File path required to be removed.

    Returns:
        str: delete path
    """
    return os.remove(path)


def create_empty_file(filename):
    """ Create An Empty File.

  Args:
      filename (str): file path name to be created
  """
    open(filename, "w").close()


def create_dir(newdir, unlink=False):
    """ Create New Directory.

    Args:
        newdir (str): Directory path/name.
        unlink (bool): Defaults to False.

    """
    if newdir.find("file://") != -1:
        raise RuntimeError("Cannot use file notation here")

    if exists(newdir):
        if is_link(newdir) and unlink:
            unlink(newdir)
    else:
        head, tail = os.path.split(newdir)
        if head and (not exists(head) or not is_dir(head)):
            create_dir(head, unlink=False)
        if tail:
            os.mkdir(newdir)
            # try:
            #     os.mkdir(newdir)
            #     # print "mkdir:%s"%newdir
            # except OSError as e:
            #     if e.errno != os.errno.EEXIST:  # File exists
            #         raise


def copy_dir_tree(src, dst, symlinks=False, ignore=None):
    """ Copy Tree Directory.

    Args:
        src (str): Source of tree directory.
        dst (str): destination of directory.
        symlinks (bool): Defaults to False.
        ignore (Nonetype): Defaults to None.
    """
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def change_dir(path):
    """ Changes Current Directory.

    Args:
        path (str): Directory path to be changed to.

    Returns:
        str: Current path
    """
    os.chdir(path)
    current_path = os.getcwd()

    return current_path


def move_dir(source, destin):
    """ Move Directory from source to destination.

    Args:
        source (str): Source path where the directory should be removed from
        destin (str): Destination path where the directory should be moved into
    """
    _move(source, destin)


def join_path(*args):
    """ Join one or more path components.

    Returns:
        str: Join two or more pathname components.
    """
    args = [str(x) for x in args]

    if args is None:
        raise RuntimeError("Not enough parameters %s" % (str(args)))
    if os.sys.platform.startswith("win"):
        args2 = []
        for item in args:
            item = item.replace("/", "\\")
            while len(item) > 0 and item[0] == "\\":
                item = item[1:]
            args2.append(item)
        args = args2
    return os.path.join(*args)


def get_dir_name(path, lastonly=False, levelsup=None):
    """ Return a directory name from pathname path.

    Args:
        path (str): The path to find a directory.
        lastonly (bool): Means only the last part of the path which is a dir (overrides levelsup to 0).Defaults to False.
        levelsup (NoneType): Means return the parent dir levelsup levels up. Defaults to None.

    Returns:
        str: dname + os.sep
    """

    dname = os.path.dirname(path)
    dname = dname.replace("/", os.sep)
    dname = dname.replace("//", os.sep)
    dname = dname.replace("\\", os.sep)
    if lastonly:
        dname = dname.split(os.sep)[-1]
        return dname
    if levelsup is not None:
        parts = dname.split(os.sep)
        if len(parts) - levelsup > 0:
            return parts[len(parts) - levelsup - 1]
        else:
            raise RuntimeError("Cannot find part of dir %s levels up, path %s is not long enough" % (levelsup, path))
    return dname + os.sep if dname else dname


def get_base_name(path, remove_extension=False):
    """ Return the base name of pathname path.

    Args:
        path (str): the path of the base name
        remove_extension (bool): Defaults to False.

    Returns:
        str: name
    """
    name = os.path.basename(path.rstrip(os.path.sep))
    if remove_extension:
        if "." in name:
            name = ".".join(name.split(".")[:-1])
    return name
    basename = get_base_name


def path_clean(path):
    """ Clean path.

    Args:
        path (str): source of the path of dir

    Returns:
        str: normcase path
    """

    return path.replace("\\", os.sep).replace("/", os.sep).lower()


def path_dir_clean(path):
    """ Clean Path Directory.

    Args:
        path (str): source of the path of dir

    Returns:
        str: normcase path
    """
    return os.path.normpath(path)


# NO DECORATORS HERE
def path_normalize(path):
    """ Normalize Path

    Args:
        path (str): The path to be normalize

    Returns:
        str: Return the absolute version of a path.
    """
    return os.path.normpath(path)


def path_remove_dir_part(path, toremove, remove_trailing_slash=False):
    """
    goal remove dirparts of a dirpath e,g, a basepath which is not needed
    will look for part to remove in full path but only full dirs
    """
    path = path_normalize(path)
    toremove = path_normalize(toremove)

    if path_clean(toremove) == path_clean(path):
        return ""
    path = path_clean(path)
    path = path.replace(path_dir_clean(toremove), "")
    if remove_trailing_slash:
        if len(path) > 0 and path[0] == os.sep:
            path = path[1:]
    path = path_clean(path)
    path = path_normalize(path)
    return path


def process_path_for_double_dots(path):
    """ double dots process.

    Args:
        path (str): the path for double dots process.

    Returns:
        str:
    """

    # print "process_path_for_double_dots:%s"%path
    path = path_clean(path)
    path = path.replace("\\", "/")
    result = []
    for item in path.split("/"):
        if item == "..":
            if result == []:
                raise RuntimeError("Cannot process_path_for_double_dots for paths with only ..")
            else:
                result.pop()
        else:
            result.append(item)
    return "/".join(result)


def get_parent(path):
    """Returns the parent of the path.

    Args:
        path (str): source path to get the parent.

    Returns:
        str: the parent of the path
    """
    parts = path.split(os.sep)
    if parts[-1] == "":
        parts = parts[:-1]
    parts = parts[:-1]
    if parts == [""]:
        return os.sep
    return os.sep.join(parts)


def get_parent_with_dir_name(path="", dirname=".git", die=False):
    """ looks for parent which has dirname in the parent directory.

    Args:
        path (str): Defaults to "".
        dirname (str): Defaults to ".git".
        die (bool): Defaults to False.

    Returns:
    str: the path which has the dirname or None
    """

    if path == "":
        path = getcwd()

    # first check if there is no .jsconfig in parent dirs
    curdir = copy.copy(path)
    while curdir.strip() != "":
        if exists("%s/%s" % (curdir, dirname)):
            return curdir
        # look for parent
        curdir = get_parent(curdir)
    if die:
        raise Exception("Could not find %s dir as parent of:'%s'" % (dirname, path))
    else:
        return None


def get_file_extension(path):
    """ Returns the extension of the file.

    Args:
        path (str): the path of file extension.

    Returns:
        str: file extension.
    """
    ext = os.path.splitext(path)[1]
    return ext.strip(".")


def chown(path, user, group=None):
    """

    Args:
        path (str):
        user (str):
        group (NoneType): [description]. Defaults to None.
    """
    from pwd import getpwnam
    from grp import getgrnam

    getpwnam(user)[2]
    uid = getpwnam(user).pw_uid
    if group is not None:
        gid = getgrnam(group).gr_gid
    else:
        gid = getpwnam(user).pw_gid
    os.chown(path, uid, gid)
    for root, dirs, files in os.walk(path):
        for ddir in dirs:
            path = os.path.join(root, ddir)
            try:
                os.chown(path, uid, gid)
            except Exception as e:
                if str(e).find("No such file or directory") == -1:
                    raise Exception("No such file or directory")
        for file in files:
            path = os.path.join(root, file)
            try:
                os.chown(path, uid, gid)
            except Exception as e:
                if str(e).find("No such file or directory") == -1:
                    raise Exception("No such file or directory")


def chmod(path, permissions):
    """ Change the file mode bits of each given file according to mode.

    Args:
        path (str): The path of the file.
        permissions (str): [description]

    Returns:
        [type]: [description]
    """
    if permissions > 511 or permissions < 0:
        raise RuntimeError("can't perform chmod, %s is not a valid mode" % oct(permissions))

    os.chmod(path, permissions)
    for root, dirs, files in os.walk(path):
        for ddir in dirs:
            path = os.path.join(root, ddir)
            try:
                os.chmod(path, permissions)
            except Exception as e:
                if str(e).find("No such file or directory") == -1:
                    raise RuntimeError("%s" % e)

        for file in files:
            path = os.path.join(root, file)
            try:
                os.chmod(path, permissions)
            except Exception as e:
                if str(e).find("No such file or directory") == -1:
                    raise RuntimeError("%s" % e)


def getcwd():
    """ Get Current working Directory.

    Returns:
        str: current working directory path.
    """
    return os.getcwd()


def read_link(path):
    """ Read links

    Args:
        path (str): [description]

    Returns:
        str: res
    """

    while path[-1] == "/" or path[-1] == "\\":
        path = path[:-1]

    if j.data.platform.is_linux() or j.data.platform.is_osx():
        res = os.readlink(path)
    elif j.data.platform.is_windows():
        raise RuntimeError("Cannot read_link on windows")
    else:
        raise RuntimeError("cant read link, dont understand platform")

    if res.startswith(".."):
        srcDir = get_dir_name(path)
        res = path_normalize("%s%s" % (srcDir, res))
    elif get_base_name(res) == res:
        res = join_path(get_parent(path), res)
    return res


def remove_links(path):
    """ Remove all links.

    Args:
        path (str): the path of the link
    """
    items = _list_all_in_dir(path=path, recursive=True, followsymlinks=False, listsymlinks=True)
    items = [item for item in items[0] if is_link(item)]
    for item in items:
        unlink(item)


def _list_in_dir(path, followsymlinks=True):
    """ List is Directory.

    Args:
        path (str): Directory path to list.
        followsymlinks (bool): Defaults to True.

    Returns:
        str: names
    """

    names = os.listdir(path)
    return names


def list_files_in_dir(
    path,
    recursive=False,
    filter=None,
    minmtime=None,
    maxmtime=None,
    depth=None,
    case_sensitivity="os",
    exclude=[],
    followsymlinks=False,
    listsymlinks=False,
):
    """ List of files in directory.

    Returns:
      str: list of files
    """
    if depth is not None:
        depth = int(depth)

    if depth == 0:
        depth = None
    # if depth is not None:
    #     depth+=1
    filesreturn, depth = _list_all_in_dir(
        path,
        recursive,
        filter,
        minmtime,
        maxmtime,
        depth,
        type="f",
        case_sensitivity=case_sensitivity,
        exclude=exclude,
        followsymlinks=followsymlinks,
        listsymlinks=listsymlinks,
    )
    return filesreturn


def list_files_and_dirs_in_dir(
    path,
    recursive=True,
    filter=None,
    minmtime=None,
    maxmtime=None,
    depth=None,
    type="fd",
    followsymlinks=False,
    listsymlinks=False,
):

    """Retrieves list of files found in the specified directory.

   Returns:
       str: Return Files.
    """
    if depth is not None:
        depth = int(depth)

    if depth == 0:
        depth = None
    # if depth is not None:
    #     depth+=1
    filesreturn, _ = _list_all_in_dir(
        path,
        recursive,
        filter,
        minmtime,
        maxmtime,
        depth,
        type=type,
        followsymlinks=followsymlinks,
        listsymlinks=listsymlinks,
    )
    return filesreturn


def _list_all_in_dir(
    path,
    recursive,
    filter=None,
    minmtime=None,
    maxmtime=None,
    depth=None,
    type="df",
    case_sensitivity="os",
    exclude=[],
    followsymlinks=True,
    listsymlinks=True,
):
    """

    Returns:
        [type]: return files
    """

    dircontent = _list_in_dir(path)
    filesreturn = []

    if case_sensitivity.lower() == "sensitive":
        matcher = fnmatch.fnmatchcase
    elif case_sensitivity.lower() == "insensitive":

        def matcher(fname, pattern):
            return fnmatch.fnmatchcase(fname.lower(), pattern.lower())

    else:
        matcher = fnmatch.fnmatch

    for direntry in dircontent:
        fullpath = join_path(path, direntry)

        if is_link_and_broken(fullpath):
            continue

        if followsymlinks:
            if is_link(fullpath):
                fullpath = read_link(fullpath)

        if is_file(fullpath) and "f" in type:
            includeFile = False
            if (filter is None) or matcher(direntry, filter):
                if (minmtime is not None) or (maxmtime is not None):
                    mymtime = os.stat(fullpath)[ST_MTIME]
                    if (minmtime is None) or (mymtime > minmtime):
                        if (maxmtime is None) or (mymtime < maxmtime):
                            includeFile = True
                else:
                    includeFile = True
            if includeFile:
                if exclude != []:
                    for excludeItem in exclude:
                        if matcher(direntry, excludeItem):
                            includeFile = False
                if includeFile:
                    filesreturn.append(fullpath)
        elif is_dir(fullpath):
            if "d" in type:
                # if not(listsymlinks==False and is_link(fullpath)):
                filesreturn.append(fullpath)
            if recursive:
                newdepth = depth
                if newdepth is not None and newdepth != 0:
                    newdepth = newdepth - 1
                if newdepth is None or newdepth != 0:
                    exclmatch = False
                    if exclude != []:
                        for excludeItem in exclude:
                            if matcher(fullpath, excludeItem):
                                exclmatch = True
                    if exclmatch is False:
                        if not (followsymlinks is False and is_link(fullpath, check_valid=True)):
                            r, _ = _list_all_in_dir(
                                fullpath,
                                recursive,
                                filter,
                                minmtime,
                                maxmtime,
                                depth=newdepth,
                                type=type,
                                exclude=exclude,
                                followsymlinks=followsymlinks,
                                listsymlinks=listsymlinks,
                            )
                            if len(r) > 0:
                                filesreturn.extend(r)
        # and followsymlinks==False and listsymlinks:
        elif is_link(fullpath) and followsymlinks == False and listsymlinks:
            filesreturn.append(fullpath)

    return filesreturn, depth


def get_path_of_running_function(function):
    """ Get Path of Running Function.

    Args:
        function (str): [description]

    Returns:
        str: getfile
    """
    return inspect.getfile(function)


def change_file_names(
    toreplace, replacewidth, pathtosearchin, recursive=True, filter=None, minmtime=None, maxmtime=None
):
    """ Change File Names.

Args:
    toreplace (str): [description]
    replacewidth (str): [description]
    pathtosearchin (str): [description]
    recursive (bool): [description]. Defaults to True.
    filter (NoneType): [description]. Defaults to None.
    minmtime (NoneType): [description]. Defaults to None.
    maxmtime (NoneType): [description]. Defaults to None.

Returns:
    [type]: [description]
"""

    if not toreplace:
        raise RuntimeError("Can't change file names, toreplace can't be empty")
    if not replacewidth:
        raise RuntimeError("Can't change file names, replacewidth can't be empty")
    paths = list_files_in_dir(pathtosearchin, recursive, filter, minmtime, maxmtime)
    for path in paths:
        dir_name = get_dir_name(path)
        file_name = get_base_name(path)
        new_file_name = file_name.replace(toreplace, replacewidth)
        if new_file_name != file_name:
            new_path = join_path(dir_name, new_file_name)
            rename_file(path, new_path)


def replace_words_in_files(pathtosearchin, templateengine, recursive=True, filter=None, minmtime=None, maxmtime=None):
    """ Replace words in files.

    Args:
        pathtosearchin (str):
        templateengine (str): [description]
        recursive (bool): [description]. Defaults to True.
        filter (NoneType): [description]. Defaults to None.
        minmtime (NoneType): [description]. Defaults to None.
        maxmtime (NoneType): [description]. Defaults to None.

    Returns:
        [type]: [description]
    """

    paths = list_files_in_dir(pathtosearchin, recursive, filter, minmtime, maxmtime)
    for path in paths:
        templateengine.replaceInsideFile(path)


def list_dirs_in_dir(path, recursive=False, dirnameonly=False, finddirectorysymlinks=True, followsymlinks=True):
    """ Retrieves list of directories found in the specified directory.

    Args:
        path (str): represents directory path to search in.
        recursive (bool): [description]. Defaults to False.
        dirnameonly (bool): [description]. Defaults to False.
        finddirectorysymlinks (bool): [description]. Defaults to True.
        followsymlinks (bool): [description]. Defaults to True.

    Returns:
        [type]: [description]
    """
    items = _list_in_dir(path)
    filesreturn = []
    for item in items:
        fullpath = os.path.join(path, item)
        if item.startswith("Icon"):
            continue
        if is_dir(fullpath, finddirectorysymlinks):
            if dirnameonly:
                filesreturn.append(item)
            else:
                filesreturn.append(fullpath)
        if recursive and is_dir(fullpath, followsymlinks):
            if is_link(fullpath):
                fullpath = read_link(fullpath)
            filesreturn.extend(
                list_dirs_in_dir(
                    fullpath,
                    recursive=recursive,
                    dirnameonly=dirnameonly,
                    finddirectorysymlinks=finddirectorysymlinks,
                    followsymlinks=followsymlinks,
                )
            )
    return filesreturn


def list_py_scripts_in_dir(path, recursive=True, filter="*.py"):
    """ Retrieves list of python scripts (with extension .py) in the specified directory

    Args:
        path (str): Represents the directory path.
        recursive (bool): [description]. Defaults to True.
        filter (str): [description]. Defaults to "*.py".

    Returns:
        str: result
    """
    result = []
    for file in list_files_in_dir(path, recursive=recursive, filter=filter):
        if file.endswith(".py"):
            # filename = file.split(os.sep)[-1]
            # scriptname = filename.rsplit(".", 1)[0]
            result.append(file)
    return result


def _move(source, destin):
    """ Move function.

    Args:
        source (str): [description]
        destin (str): [description]

    Raises:
        j.exceptions.IO: [description]
    """

    if not exists(source):
        raise RuntimeError("%s does not exist" % source)
    shutil.move(source, destin)


def exists(path, followlinks=True):
    """ Check if the specified path exists.

    Args:
        path (str): [description]
        followlinks (bool): [description]. Defaults to True.

    Raises:
        j.exceptions.Value: [description]

    Returns:
        [type]: [description]
    """

    if path is None:
        raise RuntimeError("Path is not passed in system.fs.exists")

    found = False
    try:
        st = os.lstat(path)
        found = True
    except (OSError, AttributeError):
        pass
    if found and followlinks and stat.S_ISLNK(st.st_mode):

        relativelink = read_link(path)
        newpath = join_path(get_parent(path), relativelink)
        return exists(newpath)
    if found:
        return True

    return False


def symlink(path, target, overwritetarget=False):
    """ Create a symbolic link.

    Args:
        path (str): Source path desired to create symbolic link.
        target (str): destination path required to create the symbolic link.
        overwritetarget (bool): [description]. Defaults to False.
    """
    if target[-1] == "/":
        target = target[:-1]

    if overwritetarget and exists(target):
        if is_link(target):
            remove(target)
        elif is_dir(target):
            remove(target)
        else:
            remove(target)

    if os.path.islink(target):
        remove(target)

    dir = get_dir_name(target)
    if not exists(dir):
        create_dir(dir)

    if j.data.platform.is_linux() or j.data.platform.is_osx():
        try:
            os.symlink(path, target)
        except Exception as e:
            os.remove(target)
            os.symlink(path, target)

    elif j.data.platform.is_windows():
        path = path.replace("+", ":")
        cmd = 'junction "%s" "%s"' % (
            path_normalize(target).replace("\\", "/"),
            path_normalize(path).replace("\\", "/"),
        )
        print(cmd)


def symlink_files_in_dir(src, dest, delete=True, includedirs=False, makeexecutable=False):
    """[summary]

    Args:
        src ([type]): [description]
        dest ([type]): [description]
        delete (bool, optional): [description]. Defaults to True.
        includedirs (bool, optional): [description]. Defaults to False.
        makeExecutable (bool, optional): [description]. Defaults to False.
    """
    if includedirs:
        items = list_files_and_dirs_in_dir(src, recursive=False, followsymlinks=False, listsymlinks=False)
    else:
        items = list_files_in_dir(src, recursive=False, followsymlinks=True, listsymlinks=True)
    for item in items:
        dest2 = "%s/%s" % (dest, get_base_name(item))
        dest2 = dest2.replace("//", "/")

        symlink(item, dest2, overwritetarget=delete)
        if makeexecutable:
            # print("executable:%s" % dest2)
            chmod(dest2, 0o770)
            chmod(item, 0o770)


def hardlink_file(source, destin):
    """[summary]

  Args:
      source ([type]): [description]
      destin ([type]): [description]

  Raises:
      j.exceptions.RuntimeError: [description]

  Returns:
      [type]: [description]
  """

    if j.data.platform.is_linux() or j.data.platform.is_osx():
        return os.link(source, destin)
    else:
        raise RuntimeError("Cannot create a hard link on windows")


def check_dir_param(path):
    """[summary]

    Args:
        path ([type]): [description]

    Raises:
        j.exceptions.Value: [description]
        j.exceptions.RuntimeError: [description]
        j.exceptions.RuntimeError: [description]
        j.exceptions.Value: [description]
        j.exceptions.Value: [description]
        j.exceptions.Value: [description]
        Exception: [description]
        Exception: [description]
        j.exceptions.NotImplemented: [description]
        j.exceptions.RuntimeError: [description]

    Returns:
        [type]: [description]
"""

    if path.strip() == "":
        raise RuntimeError("path parameter cannot be empty.")
    path = path_normalize(path)
    if path[-1] != "/":
        path = path + "/"
    return path


"""Check if the specified Directory path exists
    @param path: string
    @param followsoftlink: boolean
    @rtype: boolean (True if directory exists)
    """


def is_dir(path, followsoftlink=False):
    """[summary]

 Args:
     path ([type]): [description]
     followsoftlink (bool, optional): [description]. Defaults to False.

 Returns:
     [type]: [description]
 """

    if is_link(path):
        if not followsoftlink:
            return False
        path = read_link(path)
    return os.path.isdir(path)


def is_empty_dir(path):
    """[summary]

    Args:
        path ([type]): [description]

    Returns:
        [type]: [description]
    """

    if _list_in_dir(path) == []:

        return True

    return False


def is_file(path, followsoftlink=True):
    """[summary]

 Args:
     path ([type]): [description]
     followsoftlink (bool, optional): [description]. Defaults to True.

 Returns:
     [type]: [description]
 """

    if not followsoftlink and is_link(path):

        return True

    if os.path.isfile(path):

        return True

    return False


def is_executable(path):
    """[summary]

    Returns:
        [type]: [description]
    """
    statobj = stat_path(path, follow_symlinks=False)
    return not (stat.S_IXUSR & statobj.st_mode == 0)


def is_link_and_broken(path, remove_if_broken=True):
    """[summary]

Args:
    path ([type]): [description]
    remove_if_broken (bool, optional): [description]. Defaults to True.

Raises:
    j.exceptions.RuntimeError: [description]
    j.exceptions.RuntimeError: [description]
    j.exceptions.Value: [description]
    j.exceptions.Value: [description]
    j.exceptions.Value: [description]
    Exception: [description]
    Exception: [description]
    j.exceptions.NotImplemented: [description]
    j.exceptions.RuntimeError: [description]

Returns:
    [type]: [description]
"""

    if os.path.islink(path):
        rpath = read_link(path)
        if not exists(rpath):
            if remove_if_broken:
                remove(path)
            return True
    return False

    """Check if the specified path is a link
    @param path: string
    @rtype: boolean (True if the specified path is a link)

    @PARAM check_valid if True, will remove link if the dest is not there and return False
    """


def is_link(path, checkjunction=False, check_valid=False):
    """[summary]

    Args:
        path ([type]): [description]
        checkjunction (bool, optional): [description]. Defaults to False.
        check_valid (bool, optional): [description]. Defaults to False.

    Raises:
        j.exceptions.RuntimeError: [description]
        j.exceptions.RuntimeError: [description]

    Returns:
        [type]: [description]
    """

    if path[-1] == os.sep:
        path = path[:-1]

    if checkjunction and j.data.platform.is_windows():
        cmd = "junction %s" % path
        try:
            result = []
            # result = j.sals.process.execute(cmd)
            pass
        except Exception as e:
            raise RuntimeError("Could not execute junction cmd, is junction installed? Cmd was %s." % cmd)
        if result[0] != 0:
            raise RuntimeError("Could not execute junction cmd, is junction installed? Cmd was %s." % cmd)
        if result[1].lower().find("substitute name") != -1:
            return True
        else:
            return False

    if os.path.islink(path):
        if check_valid:
            j.shell()
        return True

    return False


def is_mount(path):
    """[summary]

    Args:
        path ([type]): [description]

    Raises:
        j.exceptions.Value: [description]

    Returns:
        [type]: [description]
    """

    if path is None:
        raise RuntimeError("Path is passed null in system.fs.isMount")
    return os.path.ismount(path)


def stat_path(path, follow_symlinks=True):
    """[summary]

Args:
    path ([type]): [description]
    follow_symlinks (bool, optional): [description]. Defaults to True.

Raises:
    j.exceptions.Value: [description]
    j.exceptions.Value: [description]
    Exception: [description]
    Exception: [description]
    j.exceptions.NotImplemented: [description]
    j.exceptions.RuntimeError: [description]

Returns:
    [type]: [description]
"""
    return os.stat(path, follow_symlinks=follow_symlinks)


def rename_dir(dirname, newname, overwrite=False):
    """[summary]

Args:
    dirname ([type]): [description]
    newname ([type]): [description]
    overwrite (bool, optional): [description]. Defaults to False.

Raises:
    j.exceptions.Value: [description]
    j.exceptions.Value: [description]
    Exception: [description]
    Exception: [description]
    j.exceptions.NotImplemented: [description]
    j.exceptions.RuntimeError: [description]

Returns:
    [type]: [description]
"""
    if dirname == newname:
        return
    if overwrite and exists(newname):
        if is_dir(newname):
            remove(newname)
        else:
            remove(newname)
    os.rename(dirname, newname)


def unlink_file(filename):
    """[summary]

    Args:
        filename ([type]): [description]
    """
    if j.data.platform.is_windows():
        cmd = "junction -d %s 2>&1 > null" % (filename)
        # _log_info(cmd)
        os.system(cmd)
    os.unlink(filename)


def unlink(filename):
    """Remove the given file if it's a file or a symlink
    @param filename: File path to be removed
    @type filename: string
    """

    if j.data.platform.is_windows():
        cmd = "junction -d %s 2>&1 > null" % (filename)
        # _log_info(cmd)
        os.system(cmd)
    os.unlink(filename)


def readfile(filename, binary=False, encoding="utf-8"):
    """ Read a file and get contents of that file.

    Args:
        filename (str): filename to open for reading
        binary (bool):  Defaults to False.
        encoding (str):  Defaults to "utf-8".

    Returns:
        str: data
    """

    if binary:
        with open(filename, mode="rb") as fp:
            data = fp.read()
    else:
        with open(filename, encoding=encoding) as fp:
            data = fp.read()
    return data


def touch(paths):
    """[summary]

   Args:
       paths ([type]): [description]
    """
    if isinstance(paths, list):
        for item in paths:
            touch(item)
    else:
        path = paths
        create_dir(get_dir_name(path))
        if not exists(path=path):
            writefile(path, "")


def writefile(filename, contents, append=False):
    """[summary]

   Args:
       filename ([type]): [description]
       contents ([type]): [description]
       append (bool, optional): [description]. Defaults to False.

   Raises:
       j.exceptions.Value: [description]
    """
    if contents is None:
        raise RuntimeError("Passed None parameters in system.fs.writefile")
    # filename = j.core.tools.text_replace(filename)
    if append is False:
        fp = open(filename, "wb")
    else:
        fp = open(filename, "ab")

    if isinstance(contents, str):
        fp.write(bytes(contents, "UTF-8"))
    else:
        fp.write(contents)
    # fp.write(contents)
    fp.close()


def file_size(filename):
    """ Get the size of the file in bytes.

    Args:
        filename (str): the name of the file that you want to know the size of it.

    Raises:
        j.exceptions.Value: [description]
        Exception: [description]
        Exception: [description]
        j.exceptions.NotImplemented: [description]
        j.exceptions.RuntimeError: [description]

    Returns:
        int : getsize filename
    """
    return os.path.getsize(filename)


def write_object_to_file(filelocation, obj):
    """write an object to a file

    Args:
        filelocation (str): location of the file.
        obj (str):

    Raises:
        j.exceptions.Value: [description]
        Exception: [description]
        Exception: [description]
    """
    if not obj:
        raise RuntimeError("You should provide a filelocation or a object as parameters")

    try:
        pcl = pickle.dumps(obj)
    except Exception as e:
        raise Exception("Could not create pickle from the object \nError: %s" % (str(e)))
    writefile(filelocation, pcl)
    if not exists(filelocation):
        raise Exception("File isn't written to the filesystem")


"""
    Read a object from a file(file contents in pickle format)
    @param filelocation: location of the file
    @return: object
    """


def read_object_from_file(filelocation):
    """[summary]

Args:
    filelocation ([type]): [description]

Raises:
    j.exceptions.NotImplemented: [description]
    j.exceptions.RuntimeError: [description]

Returns:
    [type]: [description]
"""

    file = os.open(filelocation)
    contents = file.readfile()
    file.close()
    return pickle.loads(contents)


"""Return the hex digest of a file without loading it all into memory
    @param filename: string (filename to get the hex digest of it) or list of files
    @rtype: md5 of the file
    """


def md5sum(filename):
    """[summary]

Args:
    filename ([type]): [description]

Raises:
    j.exceptions.NotImplemented: [description]
    j.exceptions.RuntimeError: [description]

Returns:
    [type]: [description]
"""

    if not isinstance(filename, list):
        filename = [filename]
    digest = hashlib.md5()
    for filepath in filename:
        with open(filepath, "rb") as fh:
            while True:
                buf = fh.read(4096)
                if buf == b"":
                    break
                digest.update(buf)
    return digest.hexdigest()


def get_folder_md5sum(folder):
    """[summary]

    Args:
        folder ([type]): [description]

    Returns:
        str: md5sum files
    """
    files = sorted(os.walk(folder))
    return md5sum(files)


def get_tmp_dir_path(name="", create=True):
    """  create a tmp dir name and makes sure the dir exists

  Args:
      name (str): [description]. Defaults to "".
      create (bool): [description]. Defaults to True.

  Returns:
      bool: tmpdir
  """
    if name:
        tmpdir = join_path(j.dirs.TMPDIR, name)
    else:
        tmpdir = join_path(j.dirs.TMPDIR, j.data.idgenerator.generateXCharID(10))
    if create is True:
        create_dir(tmpdir)
    return tmpdir


def get_tmp_file_path(cygwin=False):
    """Generate a temp file path

    Args:
        cygwin (bool): [description]. Defaults to False.

    Returns:
        [type]: [description]
    """
    tmpdir = j.dirs.TMPDIR + "/jumpscale/"
    j.sals.fs.create_dir(tmpdir)
    fd, path = tempfile.mkstemp(dir=tmpdir)
    try:
        real_fd = os.fdopen(fd)
        real_fd.close()
    except (IOError, OSError):
        pass
    if cygwin:
        path = path.replace("\\", "/")
        path = path.replace("//", "/")
    return path


def _file_path_tmp_get(ext="sh"):
    """[summary]

   Args:
       ext (str, optional): [description]. Defaults to "sh".

   Returns:
       [type]: [description]
   """
    return j.core.tools._file_path_tmp_get(ext)


def is_asxii_file(filename, checksize=4096):
    """[summary]

    Args:
        filename ([type]): [description]
        checksize (int, optional): [description]. Defaults to 4096.

    Returns:
        [type]: [description]
    """
    # TODO: let's talk about checksize feature.
    try:
        with open(filename, encoding="ascii") as f:
            f.read()
            return True
    except UnicodeDecodeError:
        return False


def is_binary_file(filename, checksize=4096):
    """[summary]

    Args:
        filename ([type]): [description]
        checksize (int, optional): [description]. Defaults to 4096.

    Returns:
        [type]: [description]
    """
    return not is_asxii_file(filename, checksize)


def is_absolute(path):
    """[summary]

    Args:
        path ([type]): [description]

    Returns:
        [type]: [description]
    """
    return os.path.isabs(path)


# THERE IS A tools.lock implementation we need to use that one
# lock = staticmethod(lock)
# lock_ = staticmethod(lock_)
# islocked = staticmethod(islocked)
# unlock = staticmethod(unlock)
# unlock_ = staticmethod(unlock_)


def validate_filename(filename, platform=None):
    """ Validate a filename for a given (or current) platform.

    Args:
        filename (str): File name to check.
        platform (Nonetype): Platform to validate against. Defaults to None.

    Raises:
        j.exceptions.NotImplemented: [description]

    Returns:
        bool: Whether the filename is valid on the given platform
    """
    platform = platform or j.core.platformtype.myplatform

    if not filename:
        return False

    # When adding more restrictions to check_unix or check_windows, please
    # update the validateFilename documentation accordingly


def check_unix(filename):
    """[summary]

    Args:
        filename ([type]): [description]

    Returns:
        [type]: [description]
    """
    if len(filename) > 255:
        return False

    if "\0" in filename or "/" in filename:
        return False

    return True


def check_windows(filename):
    """ Check windows

Args:
    filename (str):

Raises:
    j.exceptions.NotImplemented: [description]

Returns:
    [type]: [description]
"""
    if len(filename) > 255:
        return False

    if os.path.splitext(filename)[0] in ("CON", "PRN", "AUX", "CLOCK$", "NUL"):
        return False

    if os.path.splitext(filename)[0] in ("COM%d" % i for i in range(1, 9)):
        return False

    if os.path.splitext(filename)[0] in ("LPT%d" % i for i in range(1, 9)):
        return False

    # ASCII characters 0x00 - 0x1F are invalid in a Windows filename
    # We loop from 0x00 to 0x20 (xrange is [a, b[), and check whether
    # the corresponding ASCII character (which we get through the chr(i)
    # function) is in the filename
    for c in range(0x00, 0x20):
        if chr(c) in filename:
            return False

    for c in ("<", ">", ":", '"', "/", "\\", "|", "?", "*"):
        if c in filename:
            return False

    if filename.endswith((" ", ".")):
        return False

    return True

    if j.data.platform.is_windows():
        return check_windows(filename)

    if j.data.platform.is_linux():
        return check_unix(filename)

    raise RuntimeError("Filename validation on given platform not supported")


def find(startDir, fileregex):
    """ Search for files or folders matching a given pattern.

    Args:
        startDir (str): [description]
        fileregex (str): [description]

    Returns:
        str: result
    """

    result = []
    for root, dirs, files in os.walk(startDir, followlinks=True):
        for name in files:
            if fnmatch.fnmatch(name, fileregex):
                result.append(os.path.join(root, name))
    return result


def grep(fileregex, lineregex):
    """Search for lines matching a given regex in all files matching a regex

   Args:
       fileregex (str):Files to search in.
       lineregex (str): Regex pattern to search for in each file.
   """
    import glob
    import re
    import os

    for filename in glob.glob(fileregex):
        if os.path.isfile(filename):
            f = open(filename, "r")
            for line in f:
                if re.match(lineregex, line):
                    print(("%s: %s" % (filename, line)))


def construct_dir_path_from_array(array):
    """ Create a path using os specific seperators from a list being passed with directoy.

    Args:
        array (str): list of dirs in the path.

    Returns:
        str: path
    """
    path = ""
    for item in array:
        path = path + os.sep + item
    path = path + os.sep
    if j.data.platform.is_linux() or j.data.platform.is_osx():
        path = path.replace("//", "/")
        path = path.replace("//", "/")
    return path


def construct_file_path_from_array(array):
    """ Add file name  to dir path

    Args:
        array (str): list including dir path then file name

    Returns:
        str: path
    """
    path = construct_dir_path_from_array(array)
    if path[-1] == "/":
        path = path[0:-1]
    return path


def path_to_unicode(path):
    """ Convert Path to unicode.

    Args:
        path (str): the path to convert to unicode.

    Returns:
        str: unicode path
    """

    from Jumpscale.core.Dirs import Dirs

    return Dirs.path_to_unicode(path)


def targz_compress(
    sourcepath,
    destinationpath,
    followlinks=False,
    destintar="",
    pathregexincludes=[".[a-zA-Z0-9]*"],
    pathRegexExcludes=[],
    contentregexincludes=[],
    contentregexexcludes=[],
    depths=[],
    extrafiles=[],
):
    """ Compress targz.

    Args:
        sourcepath (str): Source directory.
        destinationpath (str): Destination filename.
        followlinks (bool):  do not tar the links, follow the link and add that file or content of directory to the tar. Defaults to False.
        destintar (str):  Defaults to "".
        pathregexincludes (list): Defaults to [".[a-zA-Z0-9]*"].
        pathRegexExcludes (list): [description]. Defaults to [].
        contentregexincludes (list): [description]. Defaults to [].
        contentregexexcludes (list): [description]. Defaults to [].
        depths (list): [description]. Defaults to [].
        extrafiles (list): Adds extra files to tar. Defaults to [].

    Raises:
        j.exceptions.RuntimeError: [description]
    """
    import os.path
    import tarfile

    if not exists(get_dir_name(destinationpath)):
        create_dir(get_dir_name(destinationpath))
    t = tarfile.open(name=destinationpath, mode="w:gz")
    if not (
        followlinks
        or destintar != ""
        or pathregexincludes != [".*"]
        or pathRegexExcludes != []
        or contentregexincludes != []
        or contentregexexcludes != []
        or depths != []
    ):
        t.add(sourcepath, "/")
    else:

        def addToTar(params, path):
            tarfile = params["t"]
            destintar = params["destintar"]
            destpath = join_path(destintar, path_remove_dir_part(path, sourcepath))
            if is_link(path) and followlinks:
                path = read_link(path)

            # print "fstar: add file %s to tar" % path
            if not (j.data.platform.is_windows() and j.sals.windows.checkFileToIgnore(path)):
                if is_file(path) or is_link(path):
                    tarfile.add(path, destpath)
                else:
                    raise RuntimeError("Cannot add file %s to destpath" % destpath)

        params = {}
        params["t"] = t
        params["destintar"] = destintar
        j.sals.fswalker.walk(
            root=sourcepath,
            callback=addToTar,
            arg=params,
            recursive=True,
            includeFolders=False,
            pathregexincludes=pathregexincludes,
            pathRegexExcludes=pathRegexExcludes,
            contentregexincludes=contentregexincludes,
            contentregexexcludes=contentregexexcludes,
            depths=depths,
            followlinks=False,
        )

        if extrafiles != []:
            for extrafile in extrafiles:
                source = extrafile[0]
                destpath = extrafile[1]
                t.add(source, join_path(destintar, destpath))
    t.close()


def gzip(sourcefile, destfile):
    """Gzip source file into destination zip

    Args:
        sourcefile (str): path to file to be Gzipped.
        destfile (str): path to  destination Gzip file.
    """
    import gzip

    f_in = open(sourcefile, "rb")
    f_out = gzip.open(destfile, "wb")
    f_out.writelines(f_in)
    f_out.close()
    f_in.close()


def gunzip(sourcefile, destFile):
    """Gunzip gzip sourcefile into destination file

    Args:
        sourcefile (str): path to gzip file to be unzipped.
        destFile (str): path to destination folder to unzip folder.
    """
    import gzip

    create_dir(get_dir_name(destFile))
    f_in = gzip.open(sourcefile, "rb")
    f_out = open(destFile, "wb")
    f_out.writelines(f_in)
    f_out.close()
    f_in.close()


def targz_uncompress(sourcefile, destinationdir, removedestinationdir=True):
    """ compress dirname recursive

    Args:
        sourcefile (str): file to uncompress.
        destinationdir (str): path of the destiniation directory.
        removedestinationdir (bool): [description]. Defaults to True.
    """
    if removedestinationdir:
        remove(destinationdir)
    if not exists(destinationdir):
        create_dir(destinationdir)
    import tarfile

    # The tar of python does not create empty directories.. this causes
    # many problem while installing so we choose to use the linux tar here
    if j.data.platform.is_windows():
        tar = tarfile.open(sourcefile)
        tar.extractall(destinationdir)
        tar.close()
        # todo find better alternative for windows
    else:
        cmd = "tar xzf '%s' -C '%s'" % (sourcefile, destinationdir)
        j.sals.process.execute(cmd)
