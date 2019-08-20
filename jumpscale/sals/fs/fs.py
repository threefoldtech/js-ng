import sys
import re
from jumpscale.god import j
import os
import os.path
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




def copy_file(fileFrom, to, create_dir_ifneeded=False, overwritefile=True):
    """Copy file

    Copies the file from C{fileFrom} to the file or directory C{to}.
    If C{to} is a directory, a file with the same basename as C{fileFrom} is
    created (or overwritten) in the directory specified.
    Permission bits are copied.

    @param fileFrom: Source file path name
    @type fileFrom: string
    @param to: Destination file or folder path name
    @type to: string

    @autocomplete

    """
    # Create target folder first, otherwise copy fails
    target_folder = os.path.dirname(to)
    if create_dir_ifneeded:
        create_dir(target_folder)
    if exists(to):
        if os.path.samefile(fileFrom, to):
            raise j.exceptions.Input("{src} and {dest} are the same file".format(src=fileFrom, dest=to))
        if overwritefile is False:
            if os.path.samefile(to, target_folder):
                destfilename = os.path.join(to, os.path.basename(fileFrom))
                if exists(destfilename):
                    return
            else:
                return
        elif is_file(to):
            # overwriting some open  files is frustrating and may not work
            # due to locking [delete/copy is a better strategy]
            remove(to)
    shutil.copy(fileFrom, to)
    


def move_file(source, destin):
    """Move a  File from source path to destination path
    @param source: string (Source file path)
    @param destination: string (Destination path the file should be moved to )
    """
    
    _move(source, destin)

def rename_file(filepath, new_name):
    """
    OBSOLETE
    """
    
    return _move(filepath, new_name)


def remove_irrelevant_files(path, followsymlinks=True):
    """Will remove files having extensions: pyc, bak
    @param path: string (path to search in)
    """
    ext = ["pyc", "bak"]
    for path in list_files_in_dir(path, recursive=True, followsymlinks=followsymlinks):
        if get_file_extension(path) in ext:
            remove(path)


def remove(path):
    """Remove a File
    @param path: string (File path required to be removed)
    """
    return j.core.tools.delete(path)


def create_empty_file(filename):
    """Create an empty file
    @param filename: string (file path name to be created)
    """
    
    open(filename, "w").close()
    


def create_dir(newdir, unlink=False):
    """Create new Directory
    @param newdir: string (Directory path/name)
    if newdir was only given as a directory name, the new directory will be created on the default path,
    if newdir was given as a complete path with the directory name, the new directory will be created in the specified path
    """
    if newdir.find("file://") != -1:
        raise j.exceptions.RuntimeError("Cannot use file notation here")
    
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

        

def copy_dir_tree(
    
    src,
    dst,
    keepsymlinks=False,
    deletefirst=False,
    overwritefiles=True,
    ignoredir=None,
    ignorefiles=None,
    rsync=True,
    ssh=False,
    sshport=22,
    recursive=True,
    rsyncdelete=True,
    create_dir=False,
    showout=False,
):
    """Recursively copy an entire directory tree rooted at src.
    The dst directory may already exist; if not,
    it will be created as well as missing parent directories
    @param src: string (source of directory tree to be copied)
    @param rsyncdelete will remove files on dest which are not on source (default)
    @param recursive:  recursively look in all subdirs
    :param ignoredir: the following are always in, no need to specify ['.egg-info', '.dist-info', '__pycache__']
    :param ignorefiles: the following are always in, no need to specify: ["*.egg-info","*.pyc","*.bak"]
    @param ssh:  bool (copy to remote)
    @param sshport int (ssh port)
    @param create_dir:   bool (when ssh creates parent directory)
    @param dst: string (path directory to be copied to...should not already exist)
    @param keepsymlinks: bool (True keeps symlinks instead of copying the content of the file)
    @param deletefirst: bool (Set to True if you want to erase destination first, be carefull, this can erase directories)
    @param overwritefiles: if True will overwrite files, otherwise will not overwrite when destination exists
    """

    default_ignore_dir = [".egg-info", ".dist-info", "__pycache__"]
    if ignoredir is None:
        ignoredir = []
    if ignorefiles is None:
        ignorefiles = []
    for item in default_ignore_dir:
        if item not in ignoredir:
            ignoredir.append(item)
    default_ignorefiles = ["*.egg-info", "*.pyc", "*.bak"]
    for item in default_ignorefiles:
        if item not in ignorefiles:
            ignorefiles.append(item)

    if not rsync:
        if src.find("file://") != -1 or dst.find("file://") != -1:
            raise j.exceptions.RuntimeError("Cannot use file notation here")
        
        if (src is None) or (dst is None):
            raise j.exceptions.Value(
                "Not enough parameters passed in system.fs.copy_dir_tree to copy directory from %s to %s "
                % (src, dst)
            )
        if is_dir(src):
            names = os.listdir(src)

            if not exists(dst):
                create_dir(dst)

            errors = []
            for name in names:
                # is only for the name
                name2 = name

                srcname = join_path(src, name)
                dstname = join_path(dst, name2)

                if is_dir(srcname) and name in ignoredir:
                    continue
                if is_file(srcname) and name in ignorefiles:
                    continue

                if deletefirst and exists(dstname):
                    if is_dir(dstname, False):
                        remove(dstname)
                    elif is_link(dstname):
                        unlink(dstname)

                if is_link(srcname):
                    linkto = read_link(srcname)
                    if keepsymlinks:
                        symlink(linkto, dstname, overwritefiles)
                        continue
                    else:
                        srcname = linkto
                if is_dir(srcname):
                    # print "1:%s %s"%(srcname,dstname)
                    copy_dir_tree(
                        srcname,
                        dstname,
                        keepsymlinks,
                        deletefirst,
                        overwritefiles=overwritefiles,
                        ignoredir=ignoredir,
                        ignorefiles=ignorefiles,
                    )
                if is_file(srcname):
                    # print "2:%s %s"%(srcname,dstname)
                    copy_file(srcname, dstname, create_dir_ifneeded=False, overwritefile=overwritefiles)
        else:
            raise j.exceptions.RuntimeError("Source path %s in system.fs.copy_dir_tree is not a directory" % src)
    else:
        excl = " "
        for item in ignoredir:
            excl += "--exclude '*%s/' " % item

        dstpath2 = dst.split(":")[1] if ":" in dst else dst  # OTHERWISE CANNOT WORK FOR SSH

        dstpath = dst
        dstpath = dstpath.replace("//", "/")

        src = src.replace("//", "/")

        # ":" is there to make sure we support ssh
        if ":" not in src and j.sal.fs.is_dir(src):
            if src[-1] != "/":
                src += "/"
            if dstpath[-1] != "/":
                dstpath += "/"

        cmd = "rsync --no-owner --no-group"
        if keepsymlinks:
            # -l is keep symlinks, -L follow
            cmd += " -rlt --partial %s" % excl
        else:
            cmd += " -rLt --partial %s" % excl
        if not recursive:
            cmd += ' --exclude "*/"'
        if rsyncdelete:
            cmd += " --delete --delete-excluded "
        if ssh:
            cmd += " -e 'ssh -o StrictHostKeyChecking=no -p %s' " % sshport
            if create_dir:
                cmd += "--rsync-path='mkdir -p %s && rsync' " % get_parent(dstpath2)
        else:
            create_dir(get_parent(dstpath))
        cmd += " '%s' '%s'" % (src, dst)
        cmd += " --verbose"
        # print(cmd)
        rc, out, err = j.sal.process.execute(cmd, showout=showout)


def change_dir(path):
    """Changes Current Directory
    @param path: string (Directory path to be changed to)
    """
    
    os.chdir(path)
    current_path = os.getcwd()
    
    return current_path


def move_dir(source, destin):
    """Move Directory from source to destination
    @param source: string (Source path where the directory should be removed from)
    @param destin: string (Destination path where the directory should be moved into)
    """
    
    _move(source, destin)
    

def join_path(*args):
    """Join one or more path components.
    If any component is an absolute path, all previous components are thrown away, and joining continues.
    @param path1: string
    @param path2: string
    @param path3: string
    @param .... : string
    @rtype: Concatenation of path1, and optionally path2, etc...,
    with exactly one directory separator (os.sep) inserted between components, unless path2 is empty.
    """
    args = [j.core.text.toStr(x) for x in args]
    
    if args is None:
        raise j.exceptions.Value("Not enough parameters %s" % (str(args)))
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
    """
    Return a directory name from pathname path.
    @param path the path to find a directory within
    @param lastonly means only the last part of the path which is a dir (overrides levelsup to 0)
    @param levelsup means, return the parent dir levelsup levels up
        e.g. ...get_dir_name("/opt/qbase/bin/something/test.py", levelsup=0) would return something
        e.g. ...get_dir_name("/opt/qbase/bin/something/test.py", levelsup=1) would return bin
        e.g. ...get_dir_name("/opt/qbase/bin/something/test.py", levelsup=10) would raise an error
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
            raise j.exceptions.RuntimeError(
                "Cannot find part of dir %s levels up, path %s is not long enough" % (levelsup, path)
            )
    return dname + os.sep if dname else dname


def get_base_name(path, remove_extension=False):
    """Return the base name of pathname path."""
    
    name = os.path.basename(path.rstrip(os.path.sep))
    if remove_extension:
        if "." in name:
            name = ".".join(name.split(".")[:-1])
    return name
basename = get_base_name

# NO DECORATORS HERE
def path_clean(path):
    """
    goal is to get a equal representation in / & \ in relation to os.sep
    """
    return os.path.normcase(path)

# NO DECORATORS HERE
def path_dir_clean(path):
    return os.path.normpath(path)

# NO DECORATORS HERE
def path_normalize(path):
    """
    paths are made absolute & made sure they are in line with os.sep
    @param path: path to normalize
    """
    return os.path.abspath(path)

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
    return path

def process_path_for_double_dots(path):
    """
    /root/somepath/.. would become /root
    /root/../somepath/ would become /somepath

    result will always be with / slashes
    """
    # print "process_path_for_double_dots:%s"%path
    path = path_clean(path)
    path = path.replace("\\", "/")
    result = []
    for item in path.split("/"):
        if item == "..":
            if result == []:
                raise j.exceptions.RuntimeError("Cannot process_path_for_double_dots for paths with only ..")
            else:
                result.pop()
        else:
            result.append(item)
    return "/".join(result)


def get_parent(path):
    """
    Returns the parent of the path:
    /dir1/dir2/file_or_dir -> /dir1/dir2/
    /dir1/dir2/            -> /dir1/
    """
    parts = path.split(os.sep)
    if parts[-1] == "":
        parts = parts[:-1]
    parts = parts[:-1]
    if parts == [""]:
        return os.sep
    return os.sep.join(parts)

def get_parent_with_dir_name(path="", dirname=".git", die=False):
    """
    looks for parent which has $dirname in the parent dir, if found return
    if not found will return None or die

    Raises:
        RuntimeError -- if die 

    Returns:
        string -- the path which has the dirname or None

    """
    if path == "":
        path = j.sal.fs.getcwd()

    # first check if there is no .jsconfig in parent dirs
    curdir = copy.copy(path)
    while curdir.strip() != "":
        if j.sal.fs.exists("%s/%s" % (curdir, dirname)):
            return curdir
        # look for parent
        curdir = j.sal.fs.get_parent(curdir)
    if die:
        raise j.exceptions.Base("Could not find %s dir as parent of:'%s'" % (dirname, path))
    else:
        return None


def get_file_extension(path):
    ext = os.path.splitext(path)[1]
    return ext.strip(".")


def chown(path, user, group=None):
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
                    raise j.exceptions.RuntimeError("%s" % e)
        for file in files:
            path = os.path.join(root, file)
            try:
                os.chown(path, uid, gid)
            except Exception as e:
                if str(e).find("No such file or directory") == -1:
                    raise j.exceptions.RuntimeError("%s" % e)


def chmod(path, permissions):
    """
    @param permissions e.g. 0o660 (USE OCTAL !!!)
    """
    if permissions > 511 or permissions < 0:
        raise j.exceptions.Value("can't perform chmod, %s is not a valid mode" % oct(permissions))

    os.chmod(path, permissions)
    for root, dirs, files in os.walk(path):
        for ddir in dirs:
            path = os.path.join(root, ddir)
            try:
                os.chmod(path, permissions)
            except Exception as e:
                if str(e).find("No such file or directory") == -1:
                    raise j.exceptions.RuntimeError("%s" % e)

        for file in files:
            path = os.path.join(root, file)
            try:
                os.chmod(path, permissions)
            except Exception as e:
                if str(e).find("No such file or directory") == -1:
                    raise j.exceptions.RuntimeError("%s" % e)


def path_parse(path, base_dir="", exist_check=True, checkis_file=False):
    """
    parse paths of form /root/tmp/33_adoc.doc into the path, priority which is numbers before _ at beginning of path
    also returns filename
    checks if path can be found, if not will fail
    when filename="" then is directory which has been parsed
    if base_dir specified that part of path will be removed

    example:
    j.sal.fs.path_parse("/opt/qbase3/apps/specs/myspecs/definitions/cloud/datacenter.txt","/opt/qbase3/apps/specs/myspecs/",exist_check=False)
    @param path is existing path to a file
    @param base_dir, is the absolute part of the path not required
    @return list of dirpath,filename,extension,priority
            priority = 0 if not specified
    """
    # make sure only clean path is left and the filename is out
    if exist_check and not exists(path):
        raise j.exceptions.RuntimeError("Cannot find file %s when importing" % path)
    if checkis_file and not is_file(path):
        raise j.exceptions.RuntimeError("Path %s should be a file (not e.g. a dir), error when importing" % path)
    extension = ""
    if is_dir(path):
        name = ""
        path = path_clean(path)
    else:
        name = get_base_name(path)
        path = path_clean(path)
        # make sure only clean path is left and the filename is out
        path = get_dir_name(path)
        # find extension
        regexToFindExt = "\.\w*$"
        if j.data.regex.match(regexToFindExt, name):
            extension = j.data.regex.findOne(regexToFindExt, name).replace(".", "")
            # remove extension from name
            name = j.data.regex.replace(
                regexToFindExt, regexFindsubsettoreplace=regexToFindExt, replacewidth="", text=name
            )

    if base_dir != "":
        path = path_remove_dir_part(path, base_dir)

    if name == "":
        dirOrFilename = get_dir_name(path, lastonly=True)
    else:
        dirOrFilename = name
    # check for priority
    regexToFindPriority = "^\d*_"
    if j.data.regex.match(regexToFindPriority, dirOrFilename):
        # found priority in path
        priority = j.data.regex.findOne(regexToFindPriority, dirOrFilename).replace("_", "")
        # remove priority from path
        name = j.data.regex.replace(
            regexToFindPriority, regexFindsubsettoreplace=regexToFindPriority, replacewidth="", text=name
        )
    else:
        priority = 0

    return path, name, extension, priority  # if name =="" then is dir

def getcwd():
    """get current working directory
    @rtype: string (current working directory path)
    """
    
    return os.getcwd()


def read_link(path):
    """Works only for unix
    Return a string representing the path to which the symbolic link points.
    returns the source location (non relative)
    """
    while path[-1] == "/" or path[-1] == "\\":
        path = path[:-1]
    
    if j.core.platformtype.myplatform.platform_is_unix or j.core.platformtype.myplatform.platform_is_osx:
        res = os.readlink(path)
    elif j.core.platformtype.myplatform.platform_is_windows:
        raise j.exceptions.RuntimeError("Cannot read_link on windows")
    else:
        raise j.exceptions.Base("cant read link, dont understand platform")

    if res.startswith(".."):
        srcDir = get_dir_name(path)
        res = path_normalize("%s%s" % (srcDir, res))
    elif get_base_name(res) == res:
        res = join_path(get_parent(path), res)
    return res


def remove_links(path):
    """
    find all links & remove
    """
    items = _list_all_in_dir(path=path, recursive=True, followsymlinks=False, listsymlinks=True)
    items = [item for item in items[0] if is_link(item)]
    for item in items:
        unlink(item)

def _list_in_dir(path, followsymlinks=True):
    """returns array with dirs & files in directory
    @param path: string (Directory path to list contents under)
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
    """Retrieves list of files found in the specified directory
    @param path:       directory path to search in
    @type  path:       string
    @param recursive:  recursively look in all subdirs
    @type  recursive:  boolean
    @param filter:     unix-style wildcard (e.g. *.py) - this is not a regular expression
    @type  filter:     string
    @param minmtime:   if not None, only return files whose last modification time > minmtime (epoch in seconds)
    @type  minmtime:   integer
    @param maxmtime:   if not None, only return files whose last modification time < maxmtime (epoch in seconds)
    @Param depth: is levels deep wich we need to go
    @type  maxmtime:   integer
    @Param exclude: list of std filters if matches then exclude
    @rtype: list
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
    """Retrieves list of files found in the specified directory
    @param path:       directory path to search in
    @type  path:       string
    @param recursive:  recursively look in all subdirs
    @type  recursive:  boolean
    @param filter:     unix-style wildcard (e.g. *.py) - this is not a regular expression
    @type  filter:     string
    @param minmtime:   if not None, only return files whose last modification time > minmtime (epoch in seconds)
    @type  minmtime:   integer
    @param maxmtime:   if not None, only return files whose last modification time < maxmtime (epoch in seconds)
    @Param depth: is levels deep wich we need to go
    @type  maxmtime:   integer
    @param type is string with f & d inside (f for when to find files, d for when to find dirs)
    @rtype: list
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
    # There are 3 possible options for case-sensitivity for file names
    # 1. `os`: the same behavior as the OS
    # 2. `sensitive`: case-sensitive comparison
    # 3. `insensitive`: case-insensitive comparison
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
    return inspect.getfile(function)

def change_file_names(
    toreplace, replacewidth, pathtosearchin, recursive=True, filter=None, minmtime=None, maxmtime=None
):
    """
    @param toreplace e.g. {name}
    @param replace with e.g. "jumpscale"
    """
    if not toreplace:
        raise j.exceptions.Value("Can't change file names, toreplace can't be empty")
    if not replacewidth:
        raise j.exceptions.Value("Can't change file names, replacewidth can't be empty")
    paths = list_files_in_dir(pathtosearchin, recursive, filter, minmtime, maxmtime)
    for path in paths:
        dir_name = get_dir_name(path)
        file_name = get_base_name(path)
        new_file_name = file_name.replace(toreplace, replacewidth)
        if new_file_name != file_name:
            new_path = join_path(dir_name, new_file_name)
            rename_file(path, new_path)

def replace_words_in_files(
    pathtosearchin, templateengine, recursive=True, filter=None, minmtime=None, maxmtime=None
):
    """
    apply templateengine to list of found files
    @param templateengine =te  #example below
        te=j.tools.code.template_engine_get()
        te.add("name",a.name)
        te.add("description",ayses.description)
        te.add("version",ayses.version)
    """
    paths = list_files_in_dir(pathtosearchin, recursive, filter, minmtime, maxmtime)
    for path in paths:
        templateengine.replaceInsideFile(path)


def list_dirs_in_dir(path, recursive=False, dirnameonly=False, finddirectorysymlinks=True, followsymlinks=True):
    """ Retrieves list of directories found in the specified directory
    @param path: string represents directory path to search in
    @rtype: list
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
    @param path: string represents the directory path to search in
    @rtype: list
    """
    result = []
    for file in list_files_in_dir(path, recursive=recursive, filter=filter):
        if file.endswith(".py"):
            # filename = file.split(os.sep)[-1]
            # scriptname = filename.rsplit(".", 1)[0]
            result.append(file)
    return result


def _move(source, destin):
    """Main Move function
    @param source: string (If the specified source is a File....Calls move_file function)
    (If the specified source is a Directory....Calls move_dir function)
    """
    if not exists(source):
        raise j.exceptions.IO("%s does not exist" % source)
    shutil.move(source, destin)


def exists(path, followlinks=True):
    """Check if the specified path exists
    @param path: string
    @rtype: boolean (True if path refers to an existing path)
    """
    if path is None:
        raise j.exceptions.Value("Path is not passed in system.fs.exists")

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
    """Create a symbolic link
    @param path: source path desired to create a symbolic link for
    @param target: destination path required to create the symbolic link at
    @param overwritetarget: boolean indicating whether target can be overwritten
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

    if j.core.platformtype.myplatform.platform_is_unix or j.core.platformtype.myplatform.platform_is_osx:
        
        os.symlink(path, target)
    elif j.core.platformtype.myplatform.platform_is_windows:
        path = path.replace("+", ":")
        cmd = 'junction "%s" "%s"' % (
            path_normalize(target).replace("\\", "/"),
            path_normalize(path).replace("\\", "/"),
        )
        print(cmd)
        j.sal.process.execute(cmd)


def symlink_files_in_dir(src, dest, delete=True, includedirs=False, makeExecutable=False):
    if includedirs:
        items = list_files_and_dirs_in_dir(src, recursive=False, followsymlinks=False, listsymlinks=False)
    else:
        items = list_files_in_dir(src, recursive=False, followsymlinks=True, listsymlinks=True)
    for item in items:
        dest2 = "%s/%s" % (dest, get_base_name(item))
        dest2 = dest2.replace("//", "/")
        
        symlink(item, dest2, overwritetarget=delete)
        if makeExecutable:
            # print("executable:%s" % dest2)
            chmod(dest2, 0o770)
            chmod(item, 0o770)


def hardlink_file(source, destin):
    """Create a hard link pointing to source named destin. Availability: Unix.
    @param source: string
    @param destin: string
    @rtype: concatenation of dirname, and optionally linkname, etc.
    with exactly one directory separator (os.sep) inserted between components, unless path2 is empty
    """
    
    if j.core.platformtype.myplatform.platform_is_unix or j.core.platformtype.myplatform.platform_is_osx:
        return os.link(source, destin)
    else:
        raise j.exceptions.RuntimeError("Cannot create a hard link on windows")


def check_dir_param(path):
    if path.strip() == "":
        raise j.exceptions.Value("path parameter cannot be empty.")
    path = path_normalize(path)
    if path[-1] != "/":
        path = path + "/"
    return path


def is_dir(path, followsoftlink=False):
    """Check if the specified Directory path exists
    @param path: string
    @param followsoftlink: boolean
    @rtype: boolean (True if directory exists)
    """
    if is_link(path):
        if not followsoftlink:
            return False
        path = read_link(path)
    return os.path.isdir(path)


def is_empty_dir(path):
    """Check if the specified directory path is empty
    @param path: string
    @rtype: boolean (True if directory is empty)
    """
    if _list_in_dir(path) == []:
        
        return True
    
    return False


def is_file(path, followsoftlink=True):
    """Check if the specified file exists for the given path
    @param path: string
    @param followsoftlink: boolean
    @rtype: boolean (True if file exists for the given path)
    """
    
    if not followsoftlink and is_link(path):
        
        return True

    if os.path.isfile(path):
        
        return True

    
    return False


def is_executable(path):
    statobj = stat_path(path, follow_symlinks=False)
    return not (stat.S_IXUSR & statobj.st_mode == 0)

def is_link_and_broken(path, remove_if_broken=True):
    if os.path.islink(path):
        rpath = read_link(path)
        if not exists(rpath):
            if remove_if_broken:
                j.sal.fs.remove(path)
            return True
    return False


def is_link(path, checkjunction=False, check_valid=False):
    """Check if the specified path is a link
    @param path: string
    @rtype: boolean (True if the specified path is a link)

    @PARAM check_valid if True, will remove link if the dest is not there and return False
    """
    if path[-1] == os.sep:
        path = path[:-1]

    if checkjunction and j.core.platformtype.myplatform.platform_is_windows:
        cmd = "junction %s" % path
        try:
            result = j.sal.process.execute(cmd)
        except Exception as e:
            raise j.exceptions.RuntimeError(
                "Could not execute junction cmd, is junction installed? Cmd was %s." % cmd
            )
        if result[0] != 0:
            raise j.exceptions.RuntimeError(
                "Could not execute junction cmd, is junction installed? Cmd was %s." % cmd
            )
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
    """Return true if pathname path is a mount point:
    A point in a file system where a different file system has been mounted.
    """
    
    if path is None:
        raise j.exceptions.Value("Path is passed null in system.fs.isMount")
    return os.path.ismount(path)


def stat_path(path, follow_symlinks=True):
    """Perform a stat() system call on the given path
    @rtype: object whose attributes correspond to the members of the stat structure
    """
    return os.stat(path, follow_symlinks=follow_symlinks)


def rename_dir(dirname, newname, overwrite=False):
    """Rename Directory from dirname to newname
    @param dirname: string (Directory original name)
    @param newname: string (Directory new name to be changed to)
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
    """Remove the file path (only for files, not for symlinks)
    @param filename: File path to be removed
    """
    
    os.unlink(filename)


def unlink(filename):
    """Remove the given file if it's a file or a symlink

    @param filename: File path to be removed
    @type filename: string
    """
    

    if j.core.platformtype.myplatform.platform_is_windows:
        cmd = "junction -d %s 2>&1 > null" % (filename)
        #_log_info(cmd)
        os.system(cmd)
    os.unlink(filename)


def readfile(filename, binary=False, encoding="utf-8"):
    """Read a file and get contents of that file
    @param filename: string (filename to open for reading )
    @rtype: string representing the file contents
    @param encoding utf-8 or ascii
    """
    
    if binary:
        with open(filename, mode="rb") as fp:
            data = fp.read()
    else:
        with open(filename, encoding=encoding) as fp:
            data = fp.read()
    return data

def touch(paths):
    """
    can be single path or multiple (then list)
    """
    if j.data.types.list.check(paths):
        for item in paths:
            touch(item)
    path = paths
    create_dir(get_dir_name(path))
    if not exists(path=path):
        writefile(path, "")


def writefile(filename, contents, append=False):
    """
    Open a file and write file contents, close file afterwards
    @param contents: string (file contents to be written)
    """
    if contents is None:
        raise j.exceptions.Value("Passed None parameters in system.fs.writefile")
    filename = j.core.tools.text_replace(filename)
    if append is False:
        fp = open(filename, "wb")
    else:
        fp = open(filename, "ab")
    
    if j.data.types.string.check(contents):
        fp.write(bytes(contents, "UTF-8"))
    else:
        fp.write(contents)
    # fp.write(contents)
    fp.close()


def file_size(filename):
    """Get file_size of file in bytes
    @param filename: the file u want to know the file_size of
    @return: int representing file size
    """
    return os.path.getsize(filename)


def write_object_to_file(filelocation, obj):
    """
    Write a object to a file(pickle format)
    @param filelocation: location of the file to which we write
    @param obj: object to pickle and write to a file
    """
    if not obj:
        raise j.exceptions.Value("You should provide a filelocation or a object as parameters")
    
    try:
        pcl = pickle.dumps(obj)
    except Exception as e:
        raise Exception("Could not create pickle from the object \nError: %s" % (str(e)))
    writefile(filelocation, pcl)
    if not exists(filelocation):
        raise Exception("File isn't written to the filesystem")


def read_object_from_file(filelocation):
    """
    Read a object from a file(file contents in pickle format)
    @param filelocation: location of the file
    @return: object
    """
    
    file=os.open(filelocation)
    contents=file.readfile()
    file.close()
    return pickle.loads(contents)


def md5sum(filename):
    """Return the hex digest of a file without loading it all into memory
    @param filename: string (filename to get the hex digest of it) or list of files
    @rtype: md5 of the file
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
    files = sorted(os.walk(folder))
    return md5sum(files)

def get_tmp_dir_path(name="", create=True):
    """
    create a tmp dir name and makes sure the dir exists
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
    Located in temp dir of qbase
    @rtype: string representing the path of the temp file generated
    """
    tmpdir = j.dirs.TMPDIR + "/jumpscale/"
    j.sal.fs.create_dir(tmpdir)
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
    return j.core.tools._file_path_tmp_get(ext)


def is_asxii_file(filename, checksize=4096):
    # TODO: let's talk about checksize feature.
    try:
        with open(filename, encoding="ascii") as f:
            f.read()
            return True
    except UnicodeDecodeError:
        return False


def is_binary_file(filename, checksize=4096):
    return not is_asxii_file(filename, checksize)


def is_absolute(path):
    return os.path.isabs(path)

# THERE IS A tools.lock implementation we need to use that one
# lock = staticmethod(lock)
# lock_ = staticmethod(lock_)
# islocked = staticmethod(islocked)
# unlock = staticmethod(unlock)
# unlock_ = staticmethod(unlock_)


def validate_filename(filename, platform=None):
    """Validate a filename for a given (or current) platform

    Check whether a given filename is valid on a given platform, or the
    current platform if no platform is specified.

    Rules
    =====
    Generic
    -------
    Zero-length filenames are not allowed

    Unix
    ----
    Filenames can contain any character except 0x00. We also disallow a
    forward slash ('/') in filenames.

    Filenames can be up to 255 characters long.

    Windows
    -------
    Filenames should not contain any character in the 0x00-0x1F range, '<',
    '>', ':', '"', '/', '\', '|', '?' or '*'. Names should not end with a
    dot ('.') or a space (' ').

    Several basenames are not allowed, including CON, PRN, AUX, CLOCK$,
    NUL, COM[1-9] and LPT[1-9].

    Filenames can be up to 255 characters long.

    Information sources
    ===================
    Restrictions are based on information found at these URLs:

        * http://en.wikipedia.org/wiki/Filename
        * http://msdn.microsoft.com/en-us/library/aa365247.aspx
        * http://www.boost.org/doc/libs/1_35_0/libs/filesystem/doc/portability_guide.htm
        * http://blogs.msdn.com/brian_dewey/archive/2004/01/19/60263.aspx

    @param filename: Filename to check
    @type filename: string
    @param platform: Platform to validate against
    @type platform: L{PlatformType}

    @returns: Whether the filename is valid on the given platform
    @rtype: bool
    """
    platform = platform or j.core.platformtype.myplatform

    if not filename:
        return False

    # When adding more restrictions to check_unix or check_windows, please
    # update the validateFilename documentation accordingly

    def check_unix(filename):
        if len(filename) > 255:
            return False

        if "\0" in filename or "/" in filename:
            return False

        return True

    def check_windows(filename):
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

    if platform.platform_is_windows:
        return check_windows(filename)

    if platform.platform_is_unix:
        return check_unix(filename)

    raise j.exceptions.NotImplemented("Filename validation on given platform not supported")


def find(startDir, fileregex):
    """Search for files or folders matching a given pattern
    example: find("*.pyc")
    @param fileregex: The regex pattern to match
    @type fileregex: string
    """
    result = []
    for root, dirs, files in os.walk(startDir, followlinks=True):
        for name in files:
            if fnmatch.fnmatch(name, fileregex):
                result.append(os.path.join(root, name))
    return result

def grep(fileregex, lineregex):
    """Search for lines matching a given regex in all files matching a regex

    @param fileregex: Files to search in
    @type fileregex: string
    @param lineregex: Regex pattern to search for in each file
    @type lineregex: string
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
    """
    Create a path using os specific seperators from a list being passed with directoy.

    @param array str: list of dirs in the path.
    """
    path = ""
    for item in array:
        path = path + os.sep + item
    path = path + os.sep
    if j.core.platformtype.myplatform.platform_is_unix or j.core.platformtype.myplatform.platform_is_osx:
        path = path.replace("//", "/")
        path = path.replace("//", "/")
    return path

def construct_file_path_from_array(array):
    """
    Add file name  to dir path.

    @param array str: list including dir path then file name
    """
    path = construct_dir_path_from_array(array)
    if path[-1] == "/":
        path = path[0:-1]
    return path

def path_to_unicode(path):
    """
    Convert path to unicode. Use the local filesystem encoding. Will return
    path unmodified if path already is unicode.

    Use this to convert paths you received from the os module to unicode.

    @param path: path to convert to unicode
    @type path: basestring
    @return: unicode path
    @rtype: unicode
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
    """
    @param sourcepath: Source directory .
    @param destination: Destination filename.
    @param followlinks: do not tar the links, follow the link and add that file or content of directory to the tar
    @param pathregexincludes: / Excludes  match paths to array of regex expressions (array(strings))
    @param contentregexincludes: / Excludes match content of files to array of regex expressions (array(strings))
    @param depths: array of depth values e.g. only return depth 0 & 1 (would mean first dir depth and then 1 more deep) (array(int))
    @param destintar when not specified the dirs, files under sourcedirpath will be added to root of
                tar.gz with this param can put something in front e.g. /qbase3/ prefix to dest in tgz
    @param extrafiles is array of array [[source,destpath],[source,destpath],...]  adds extra files to tar
    (TAR-GZ-Archive *.tar.gz)
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
            if not (j.core.platformtype.myplatform.platform_is_windows and j.sal.windows.checkFileToIgnore(path)):
                if is_file(path) or is_link(path):
                    tarfile.add(path, destpath)
                else:
                    raise j.exceptions.RuntimeError("Cannot add file %s to destpath" % destpath)

        params = {}
        params["t"] = t
        params["destintar"] = destintar
        j.sal.fswalker.walk(
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
    """
    Gzip source file into destination zip

    @param sourcefile str: path to file to be Gzipped.
    @param destFile str: path to  destination Gzip file.
    """
    import gzip

    f_in = open(sourcefile, "rb")
    f_out = gzip.open(destFile, "wb")
    f_out.writelines(f_in)
    f_out.close()
    f_in.close()


def gunzip(sourcefile, destFile):
    """
    Gunzip gzip sourcefile into destination file

    @param sourcefile str: path to gzip file to be unzipped.
    @param destFile str: path to destination folder to unzip folder.
    """
    import gzip

    create_dir(get_dir_name(destFile))
    f_in = gzip.open(sourcefile, "rb")
    f_out = open(destFile, "wb")
    f_out.writelines(f_in)
    f_out.close()
    f_in.close()


def targz_uncompress(sourcefile, destinationdir, removedestinationdir=True):
    """
    compress dirname recursive
    @param sourcefile: file to uncompress
    @param destinationpath: path of to destiniation dir, sourcefile will end up uncompressed in destination dir
    """
    if removedestinationdir:
        remove(destinationdir)
    if not exists(destinationdir):
        create_dir(destinationdir)
    import tarfile

    # The tar of python does not create empty directories.. this causes
    # many problem while installing so we choose to use the linux tar here
    if j.core.platformtype.myplatform.platform_is_windows:
        tar = tarfile.open(sourcefile)
        tar.extractall(destinationdir)
        tar.close()
        # todo find better alternative for windows
    else:
        cmd = "tar xzf '%s' -C '%s'" % (sourcefile, destinationdir)
        j.sal.process.execute(cmd)
