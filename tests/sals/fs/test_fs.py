import pytest
import tempfile
import os
from jumpscale.god import j


def make_temps():
    old_folder_path = tempfile.mkdtemp()
    new_folder_path = tempfile.mkdtemp()
    f = tempfile.NamedTemporaryFile(dir=old_folder_path)
    return old_folder_path, new_folder_path, f


def test_copy_file():
    old_folder_path, new_folder_path, f = make_temps()
    j.sals.fs.copy_file(os.path.join(old_folder_path, f.name), new_folder_path)
    assert os.path.isfile(os.path.join(new_folder_path, os.path.basename(f.name)))


def test_move_file():
    old_folder_path, new_folder_path, f = make_temps()
    j.sals.fs.move_file(os.path.join(old_folder_path, f.name), new_folder_path)
    assert os.path.isfile(os.path.join(new_folder_path, os.path.basename(f.name)))
    assert not os.path.isfile(os.path.join(old_folder_path, os.path.basename(f.name)))


def test_rename_file():
    old_folder_path, new_folder_path, f = make_temps()
    j.sals.fs.rename_file(f.name, os.path.join(old_folder_path, "omar.txt"))
    assert os.path.isfile(os.path.join(old_folder_path, "omar.txt"))


def test_remove_irrelevant_files():
    folder = tempfile.mkdtemp()
    f1 = open(os.path.join(folder, "test.pyc"), "w")
    f2 = open(os.path.join(folder, "test.bak"), "w")
    f3 = open(os.path.join(folder, "test.txt"), "w")
    f1.close()
    f2.close()
    f3.close()
    j.sals.fs.remove_irrelevant_files(folder)
    assert not os.path.isfile(f1.name)
    assert not os.path.isfile(f2.name)
    assert os.path.isfile(f3.name)


def test_remove():
    f = tempfile.NamedTemporaryFile()
    j.sals.fs.remove(f.name)
    assert not os.path.isfile(f.name)


def test_create_empty_file():
    folder = tempfile.mkdtemp()
    j.sals.fs.create_empty_file(os.path.join(folder, "hi.txt"))
    assert os.path.isfile(os.path.join(folder, "hi.txt"))


def test_create_dir():
    root = tempfile.mkdtemp()
    j.sals.fs.create_dir(os.path.join(root, "nfolder"))
    assert os.path.isdir(os.path.join(root, "nfolder"))


def test_copy_dir_tree():
    old_folder_path, new_folder_path, f = make_temps()
    os.makedirs(os.path.join(old_folder_path, "branch1", "branch2", "branch3"))
    j.sals.fs.copy_dir_tree(old_folder_path, new_folder_path)
    assert os.path.isdir(os.path.join(new_folder_path, "branch1", "branch2", "branch3"))


def test_change_dir():
    folder = tempfile.mkdtemp()
    j.sals.fs.change_dir(folder)
    assert os.getcwd() == folder


def test_move_dir():
    old_folder_path, new_folder_path, f = make_temps()
    os.mkdir(os.path.join(old_folder_path, "folder"))
    j.sals.fs.move_dir(os.path.join(old_folder_path, "folder"), new_folder_path)
    assert not os.path.isdir(os.path.join(old_folder_path, "folder"))
    assert os.path.isdir(os.path.join(new_folder_path, "folder"))


def test_join_path():
    assert j.sals.fs.join_path("/home/user/pics", "animals", "cats") == os.path.join(
        "/home/user/pics", "animals", "cats"
    )


def test_get_dir_name():
    assert j.sals.fs.get_dir_name("home/user/docs") == "home/user/"


def test_get_base_name():
    assert j.sals.fs.get_base_name("home/user/docs") == "docs"


def test_path_clean():
    p = "home/user/pics\\animal\CaTs"
    assert j.sals.fs.path_clean(p) == "home/user/pics/animal/cats"


def test_path_remove_dir_part():
    p = "home/user/pics/animal/cats"
    assert j.sals.fs.path_remove_dir_part(p, "pics/animal") == "home/user/cats"


def test_get_parent():
    assert j.sals.fs.get_parent("dir1/dir2/dir3") == "dir1/dir2"


def test_get_file_extension():
    assert j.sals.fs.get_file_extension("home/user/docs/book.pdf") == "pdf"


# TODO test chown(), chmod() , remove_link() , is_link()


def test_list_files_and_dirs_in_dir():
    folder = tempfile.mkdtemp()
    f1 = open(os.path.join(folder, "test1.txt"), "w")
    f2 = open(os.path.join(folder, "test2.txt"), "w")
    f3 = open(os.path.join(folder, "test3.txt"), "w")
    f1.close()
    f2.close()
    f3.close()
    l = j.sals.fs.list_files_in_dir(folder)
    assert os.path.join(folder, "test1.txt") in l
    assert os.path.join(folder, "test2.txt") in l
    assert os.path.join(folder, "test3.txt") in l
    assert not os.path.join(folder, "test15.txt") in l
    os.mkdir(os.path.join(folder, "omar"))
    l = j.sals.fs.list_files_and_dirs_in_dir(folder)
    assert os.path.join(folder, "test1.txt") in l
    assert os.path.join(folder, "test2.txt") in l
    assert os.path.join(folder, "test3.txt") in l
    assert os.path.join(folder, "omar") in l
    assert not os.path.join(folder, "test15.txt") in l
    l = j.sals.fs.list_dirs_in_dir(folder)
    assert os.path.join(folder, "omar") in l
    assert not os.path.join(folder, "ahmed") in l


def test_sym_and_read_link():
    dst, src, f = make_temps()
    j.sals.fs.symlink(src, f.name)
    assert src == j.sals.fs.read_link(f.name)


def test_get_path_of_running_function():
    assert os.path.basename(j.sals.fs.get_path_of_running_function(make_temps)) == "test_fs.py"


# TODO test change_file_names() , replace_words_in_files()


def test_list_py_scripts_in_dir():
    folder = tempfile.mkdtemp()
    f1 = open(os.path.join(folder, "test1.py"), "w")
    f2 = open(os.path.join(folder, "test2.py"), "w")
    f3 = open(os.path.join(folder, "test3.txt"), "w")
    f1.close()
    f2.close()
    f3.close()
    l = j.sals.fs.list_py_scripts_in_dir(folder)
    assert os.path.join(folder, "test1.py") in l
    assert os.path.join(folder, "test2.py") in l
    assert not os.path.join(folder, "test3.txt") in l
    assert not os.path.join(folder, "test15.txt") in l


def test_exists():
    tmp = tempfile.NamedTemporaryFile()
    assert j.sals.fs.exists(tmp.name)
    assert not j.sals.fs.exists("/fdg/sdfs/sdff/sfdsf/sfdsf")


def test_symlink_files_in_dir():
    folder = tempfile.mkdtemp()
    f1 = open(os.path.join(folder, "test1.txt"), "w")
    f2 = open(os.path.join(folder, "test2.txt"), "w")
    f1.close()
    f2.close()
    dst = tempfile.mkdtemp()
    l = j.sals.fs.symlink_files_in_dir(folder, dst)
    assert os.readlink(os.path.join(dst, "test1.txt")) == os.path.join(folder, "test1.txt")
    assert os.readlink(os.path.join(dst, "test2.txt")) == os.path.join(folder, "test2.txt")


# TODO can't test hardlink_file() cause of permissions


def test_check_dir_param():
    p1 = "/sdfsdf/sfew/fcsf/"
    p2 = "/fsfs/ewf/fsfe"
    assert j.sals.fs.check_dir_param(p1) == p1
    assert j.sals.fs.check_dir_param(p2) == p2 + "/"


def test_is_dir():
    assert j.sals.fs.is_dir(tempfile.mkdtemp())
    assert not j.sals.fs.is_dir("adw/adwq/cesf/fswe/ewcde/ewcseswc/wsd/ws")


def test_is_empty_dir():
    d = tempfile.mkdtemp()
    assert j.sals.fs.is_empty_dir(d)
    f = tempfile.NamedTemporaryFile(dir=d)
    assert not j.sals.fs.is_empty_dir(d)


def test_is_file():
    old_folder_path, new_folder_path, f = make_temps()
    assert j.sals.fs.is_file(f.name)
    assert not j.sals.fs.is_file(old_folder_path)
    assert not j.sals.fs.is_file(os.path.join(new_folder_path, "omar.txt"))


# TODO test is_executable() , is_link_and_broken() , is_mount()

def test_is_link():
    f=tempfile.NamedTemporaryFile()
    d=tempfile.NamedTemporaryFile()
    j.sals.fs.symlink(d.name,f.name)
    assert j.sals.fs.is_link(f.name)

def test_stat_path():
    f=tempfile.NamedTemporaryFile()
    s=str(j.sals.fs.stat_path(f.name))
    assert 'st_size' in s and 'st_dev' in s and 'st_uid' in s

def test_rename_dir():
    d=tempfile.mkdtemp()
    dd=os.path.join(d,'ahmed')
    os.mkdir(dd)
    j.sals.fs.rename_dir(dd,os.path.join(d,'omar'))
    assert os.path.isdir(os.path.join(d,'omar'))

def test_unlink_file():
    f=tempfile.NamedTemporaryFile()
    j.sals.fs.unlink_file(f.name)
    assert not os.path.isfile(f.name)

def test_unlink():
    f=tempfile.NamedTemporaryFile()
    j.sals.fs.unlink(f.name)
    assert not os.path.isfile(f.name)

def test_readfile():
    d=tempfile.mkdtemp()
    f=os.path.join(d,'omar.txt')
    with open(f,'w') as file:
        file.write('hello there !')
    assert j.sals.fs.readfile(f)=='hello there !'

def test_touch():
    d=tempfile.mkdtemp()
    f1=os.path.join(d,'test1.txt')
    f2=os.path.join(d,'test2.txt')
    f3=os.path.join(d,'test3.txt')
    l=[f1,f2,f3]
    j.sals.fs.touch(l)
    assert os.path.isfile(f1)
    assert os.path.isfile(f2)
    assert os.path.isfile(f3)

def test_writefile():
    f=tempfile.NamedTemporaryFile()
    j.sals.fs.writefile(f.name,'hi there')
    with open(f.name,'r') as file:
        assert file.read()=='hi there'

def test_file_size():
    assert isinstance(j.sals.fs.file_size(tempfile.NamedTemporaryFile().name),int)