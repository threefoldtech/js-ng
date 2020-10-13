from tests.base_tests import BaseTests
from jumpscale.loader import j
from unittest import skip
from uuid import uuid4
import pickle
import os
import datetime
from parameterized import parameterized


class TestFS(BaseTests):
    @classmethod
    def setUpClass(cls):
        cls.temp_path = j.sals.fs.join_paths("/tmp", cls.generate_random_text())

    @classmethod
    def tearDownClass(cls):
        j.sals.fs.rmtree(cls.temp_path)

    def create_tree(self):
        self.info("Create tree")
        random_dir_dest = j.sals.fs.join_paths(self.temp_path, self.generate_random_text())
        random_dir_dest_2 = j.sals.fs.join_paths(random_dir_dest, self.generate_random_text())
        j.sals.fs.mkdirs(random_dir_dest_2)
        self.info("Create dirs {}".format(random_dir_dest_2))

        random_files = []
        random_files_internal = []
        for _ in range(5):
            random_file = j.sals.fs.join_paths(random_dir_dest, self.generate_random_text())
            self.info("Create {} file".format(random_file))
            j.sals.fs.touch(random_file)
            random_files.append(random_file)

        for _ in range(5):
            random_file = j.sals.fs.join_paths(random_dir_dest_2, self.generate_random_text())
            self.info("Create {} file".format(random_file))
            j.sals.fs.touch(random_file)
            random_files_internal.append(random_file)

        return random_dir_dest, random_dir_dest_2, random_files, random_files_internal

    def test001_is_ascii_file(self):
        pass

    def test002_is_empty_dir_with_empty_folder(self):
        random_dir_path = j.sals.fs.join_paths(self.temp_path, self.generate_random_text())
        self.info("Create {} dir".format(random_dir_path))
        j.sals.fs.mkdirs(random_dir_path)
        self.info("Assert it is empty")
        self.assertTrue(j.sals.fs.is_empty_dir(random_dir_path))

    def test003_is_empty_dir_with_data(self):
        self.info("Assert /root is not empty")
        self.assertFalse(j.sals.fs.is_empty_dir("/"))

    def test004_is_empty_dir_with_file(self):
        self.info("Assert is_empty_dir with /etc/passwd raises error")
        with self.assertRaises(NotADirectoryError):
            j.sals.fs.is_empty_dir("/etc/passwd")

    def test005_rm_tree(self):
        self.info("Create a tree")
        random_dir_dest, _, _, _ = self.create_tree()

        self.info("Remove the tree {}".format(random_dir_dest))
        j.sals.fs.rmtree("/tmp/{}".format(random_dir_dest))

        self.info("Assert that the dir and the file have been deleted")
        self.assertFalse(j.sals.fs.exists("/tmp/{}".format(random_dir_dest)))

    def test006_copy_stat(self):
        pass

    def test007_copy_file(self):
        random_dir_1 = j.sals.fs.join_paths(self.temp_path, self.generate_random_text())
        random_dir_2 = j.sals.fs.join_paths(self.temp_path, self.generate_random_text())
        random_file = self.generate_random_text()
        self.info("Create {}, {} dirs".format(random_dir_1, random_dir_2))
        j.sals.fs.mkdirs(random_dir_1)
        j.sals.fs.mkdirs(random_dir_2)

        self.info("Create random file /tmp/{}/{}".format(random_dir_1, random_file))
        src = j.sals.fs.join_paths(random_dir_1, random_file)
        dest = j.sals.fs.join_paths(random_dir_2, random_file)
        j.sals.fs.touch(src)

        self.info("Copy {} to {}".format(src, dest))
        j.sals.fs.copy_file(src, dest)

        self.info("Assert that file has been copied")
        self.assertTrue(j.sals.fs.is_file(src))
        self.assertTrue(j.sals.fs.is_file(dest))

    def test008_extension(self):
        random_file_name = "{}.py".format(self.generate_random_text())
        dest = j.sals.fs.join_paths(self.temp_path, random_file_name)

        self.info("Create random file {}".format(dest))
        j.sals.fs.touch(dest)

        self.info("Assert extension of file is correct")
        self.assertEqual(j.sals.fs.extension(dest), ".py")
        self.assertEqual(j.sals.fs.extension(dest, False), "py")

    def test009_walk(self):
        random_dir_dest, random_dir_dest_2, random_files, random_files_internal = self.create_tree()
        random_files.extend(random_files_internal)

        self.info("Assert walk with j.sals.fs.is_file as a filter works well")
        files = [file for file in j.sals.fs.walk(random_dir_dest, filter_fun=j.sals.fs.is_file)]
        for file in random_files:
            self.assertIn(file, files)

        self.info("Assert j.sals.fs.is_file filter is working well.")
        self.assertNotIn(random_dir_dest_2, files)

    def test010_walk_non_recursive(self):
        random_dir_dest, random_dir_dest_2, random_files, random_files_internal = self.create_tree()

        self.info("Assert walk non recursive with j.sals.fs.is_file as a filter works well")
        files = [file for file in j.sals.fs.walk_non_recursive(random_dir_dest, filter_fun=j.sals.fs.is_file)]
        for file in random_files:
            self.assertIn(file, files)

        for file in random_files_internal:
            self.assertNotIn(file, files)

        self.info("Assert j.sals.fs.is_file filter is working well.")
        self.assertNotIn(random_dir_dest_2, files)

    @parameterized.expand([(True,), (False,)])
    def test011_walk_files_recursive(self, recursive):
        random_dir_dest, _, random_files, random_files_internal = self.create_tree()

        self.info("Assert walk_files returns only all files with respect of recursive as {}".format(recursive))
        files = [file for file in j.sals.fs.walk_files(random_dir_dest, recursive)]
        for file in random_files:
            self.assertIn(file, files)

        for file in random_files_internal:
            if recursive:
                self.assertIn(file, files)
            else:
                self.assertNotIn(file, files)

    @parameterized.expand([(True,), (False,)])
    def test012_walk_dirs(self, recursive):
        random_dir_dest, random_dir_dest_2, _, _ = self.create_tree()
        random_dir_dest_3 = j.sals.fs.join_paths(random_dir_dest_2, self.generate_random_text())
        self.info("Create dir {}".format(random_dir_dest_3))
        j.sals.fs.mkdirs(random_dir_dest_3)

        self.info("Assert walk_dirs returns only all dirs with respect of recursive as {}".format(recursive))
        dirs = [dir_ for dir_ in j.sals.fs.walk_dirs(random_dir_dest, recursive)]

        self.assertIn(random_dir_dest_2, dirs)
        if recursive:
            self.assertEqual(2, len(dirs))
            self.assertIn(random_dir_dest_3, dirs)
        else:
            self.assertEqual(1, len(dirs))
            self.assertNotIn(random_dir_dest_3, dirs)

    def test013_path_parts(self):
        random_dir_dest_3 = j.sals.fs.join_paths(self.temp_path, self.generate_random_text())
        self.info("Create dir {}".format(random_dir_dest_3))
        parts = list(j.sals.fs.path_parts(random_dir_dest_3))
        split_path = random_dir_dest_3.split("/")
        split_path[0] = "/"
        self.assertEqual(parts, split_path)

    def test014_basename(self):
        random_dir_dest, random_dir_dest_2, _, _ = self.create_tree()
        base = self.generate_random_text()
        random_dir_dest_3 = j.sals.fs.join_paths(random_dir_dest_2, base)
        self.info("Create dir {}".format(random_dir_dest_3))

        basename = j.sals.fs.basename(random_dir_dest_3)
        self.info("Get Basename of  {}".format(random_dir_dest_3))
        self.assertEqual(basename, base)

    def test16_write_read_check_binary_file(self):
        """
        Test case for writting, reading and checking binary file.
        **Test scenario**
        #. Write binary file.
        #. Check that file has been created and it is a binary file.
        #. Read this file and check that its content.
        """
        self.info("Write binary file.")
        content = self.generate_random_text()
        random_dir_dest, random_dir_dest_2, _, _ = self.create_tree()
        random_dir_dest_3 = j.sals.fs.join_paths(random_dir_dest_2, self.generate_random_text())
        with open(random_dir_dest_3, "wb") as f:
            pickle.dump(content, f)

        self.info("Check that file has been created and it is a binary file.")
        os.path.exists(random_dir_dest_3)
        assert j.sals.fs.is_binary_file(random_dir_dest_3) is True

        self.info("Read this file and check that its content.")
        with open(random_dir_dest_3, "rb") as f:
            expected_content = f.read()
        result_content = j.sals.fs.read_binary(random_dir_dest_3)
        self.assertEqual(result_content, expected_content)

    def test_0017_create_move_rename_copy_file(self):
        """
        Test case for creating, moving, renaming and copying files.
        """
        self.info("Create an empty file.")
        random_dir_dest, random_dir_dest_2, _, _ = self.create_tree()
        file_name_1 = self.generate_random_text()
        file_path_1 = j.sals.fs.join_paths(random_dir_dest_2, file_name_1)
        j.sals.fs.write_file(file_path_1, "")

        self.info("Check that the file is exists.")
        assert os.path.exists(file_path_1) is True

        self.info("Create a directory and move this file to this directory.")
        dir_name_1 = self.generate_random_text()
        dir_path_1 = os.path.join(self.temp_path, dir_name_1)
        j.sals.fs.mkdirs(dir_path_1)
        j.sals.fs.move(file_path_1, dir_path_1)

        self.info("Check that the file is moved.")
        file_path_2 = os.path.join(dir_path_1, file_name_1)
        assert os.path.exists(file_path_2) is True
        assert os.path.exists(file_path_1) is False

        self.info("Rename this file and Check that the file is renamed.")
        file_name_2 = self.generate_random_text()
        file_path_3 = os.path.join(dir_path_1, file_name_2)
        j.sals.fs.rename(file_path_2, file_path_3)
        assert os.path.exists(file_path_3) is True
        assert os.path.exists(file_path_2) is False

        self.info("Write a word (W) to the copied file.")
        file_content = self.generate_random_text()
        j.sals.fs.write_file(file_path_3, file_content)

        self.info("Check the content of the copied file, should not be changed.")
        content_1 = j.sals.fs.read_file(file_path_3)
        assert content_1 == file_content

        self.info("Try again to copy this file to the same directory")
        j.sals.fs.write_file(file_path_3, self.generate_random_text())

        self.info("Check the content of the copied file, should be changed.")
        content_1 = j.sals.fs.read_file(file_path_3)
        assert content_1 != file_content

    def test_0018_change_file_names(self):
        """
        Test case for changing files names using j.sal.fs.change_filenames.
        """
        self.info("Create a tree with many sub directories and files with a common word (W1) in their names.")
        base_dir, _, _, _ = self.create_tree()

        self.info("Change these files names by replacing (W1) with another word (W2) ")
        log_files = [os.path.splitext(x)[0] for x in j.sals.fs.walk_files(self.temp_path) if ".log" in x]
        child_log = [os.path.splitext(os.path.join(base_dir, x))[0] for x in os.listdir(base_dir) if ".log" in x]
        j.sals.fs.change_filenames(".log", ".java", base_dir)

        self.info("Check that children files are only changed.")
        changed_files = [os.path.splitext(x)[0] for x in j.sals.fs.walk_files(self.temp_path) if ".java" in x]
        assert changed_files == child_log

        self.info("Check that files names are changed.")
        java_files = [os.path.splitext(x)[0] for x in j.sals.fs.walk_files(self.temp_path) if ".java" in x]
        assert sorted(log_files) == sorted(java_files)

        self.info("Create a new .py file")

        file_name = f"{self.generate_random_text()}.py"
        file_path = os.path.join(base_dir, file_name)
        j.sals.fs.touch(file_path)

        # self.info("Change the files names with modification time not more than 2 seconds ago.")

        # j.sals.fs.change_filenames(".py", ".html", base_dir) need to implement it .

        files_python = [x for x in j.sals.fs.walk_files(base_dir) if ".py" in x]
        assert len(files_python) == 1

    def test_019_change_name_files(self):
        """
        Test case for removing irrelevant files in a directory.
        **Test scenario**
        #. Create a tree with some directories and files.
        #. Create a file with extention bak and pyc.
        #. Change the irrelevant files, should only change files with extention bak and pyc.
        """
        self.info("Create a tree with some directories and files.")
        base_dir, _, _, _ = self.create_tree()

        self.info("Create a file with extention bak and pyc.")
        bak_file = self.generate_random_text() + ".bak"
        bak_path = os.path.join(base_dir, bak_file)
        j.sals.fs.touch(bak_path)
        pyc_file = self.generate_random_text() + ".pyc"
        pyc_path = os.path.join(base_dir, pyc_file)
        j.sals.fs.touch(pyc_path)
        dirs_files_list = [x for x in j.sals.fs.walk_files(base_dir)]

        assert bak_path in dirs_files_list
        assert pyc_path in dirs_files_list

        self.info("change the irrelevant files, should only change files with extention bak and pyc.")

        j.sals.fs.move(bak_path, os.path.join(base_dir, self.generate_random_text() + ".py"))
        j.sals.fs.move(pyc_path, os.path.join(base_dir, self.generate_random_text() + ".py"))
        dirs_files_list = [x for x in j.sals.fs.walk_files(base_dir)]

        assert bak_path not in dirs_files_list
        assert pyc_path not in dirs_files_list
