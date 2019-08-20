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

