from tests.base_tests import BaseTests
from jumpscale.loader import j
from unittest import skip
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
        random_dir_dest = j.sals.fs.join_paths(
            self.temp_path, self.generate_random_text()
        )
        random_dir_dest_2 = j.sals.fs.join_paths(
            random_dir_dest, self.generate_random_text()
        )
        j.sals.fs.mkdirs(random_dir_dest_2)
        self.info("Create dirs {}".format(random_dir_dest_2))

        random_files = []
        random_files_internal = []
        for _ in range(5):
            random_file = j.sals.fs.join_paths(
                random_dir_dest, self.generate_random_text()
            )
            self.info("Create {} file".format(random_file))
            j.sals.fs.touch(random_file)
            random_files.append(random_file)

        for _ in range(5):
            random_file = j.sals.fs.join_paths(
                random_dir_dest_2, self.generate_random_text()
            )
            self.info("Create {} file".format(random_file))
            j.sals.fs.touch(random_file)
            random_files_internal.append(random_file)

        return (
            random_dir_dest,
            random_dir_dest_2,
            random_files,
            random_files_internal,
        )

    def test001_is_ascii_file(self):
        pass

    def test002_is_empty_dir_with_empty_folder(self):
        random_dir_path = j.sals.fs.join_paths(
            self.temp_path, self.generate_random_text()
        )
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
        random_dir_1 = j.sals.fs.join_paths(
            self.temp_path, self.generate_random_text()
        )
        random_dir_2 = j.sals.fs.join_paths(
            self.temp_path, self.generate_random_text()
        )
        random_file = self.generate_random_text()
        self.info("Create {}, {} dirs".format(random_dir_1, random_dir_2))
        j.sals.fs.mkdirs(random_dir_1)
        j.sals.fs.mkdirs(random_dir_2)

        self.info(
            "Create random file /tmp/{}/{}".format(random_dir_1, random_file)
        )
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
        random_dir_dest, random_dir_dest_2, random_files, random_files_internal = (
            self.create_tree()
        )
        random_files.extend(random_files_internal)

        self.info("Assert walk with j.sals.fs.is_file as a filter works well")
        files = [
            file
            for file in j.sals.fs.walk(
                random_dir_dest, filter_fun=j.sals.fs.is_file
            )
        ]
        for file in random_files:
            self.assertIn(file, files)

        self.info("Assert j.sals.fs.is_file filter is working well.")
        self.assertNotIn(random_dir_dest_2, files)

    def test010_walk_non_recursive(self):
        random_dir_dest, random_dir_dest_2, random_files, random_files_internal = (
            self.create_tree()
        )

        self.info(
            "Assert walk non recursive with j.sals.fs.is_file as a filter works well"
        )
        files = [
            file
            for file in j.sals.fs.walk_non_recursive(
                random_dir_dest, filter_fun=j.sals.fs.is_file
            )
        ]
        for file in random_files:
            self.assertIn(file, files)

        for file in random_files_internal:
            self.assertNotIn(file, files)

        self.info("Assert j.sals.fs.is_file filter is working well.")
        self.assertNotIn(random_dir_dest_2, files)

    @parameterized.expand([(True,), (False,)])
    def test011_walk_files_recursive(self, recursive):
        random_dir_dest, _, random_files, random_files_internal = (
            self.create_tree()
        )

        self.info(
            "Assert walk_files returns only all files with respect of recursive as {}".format(
                recursive
            )
        )
        files = [
            file for file in j.sals.fs.walk_files(random_dir_dest, recursive)
        ]
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
        random_dir_dest_3 = j.sals.fs.join_paths(
            random_dir_dest_2, self.generate_random_text()
        )
        self.info("Create dir {}".format(random_dir_dest_3))
        j.sals.fs.mkdirs(random_dir_dest_3)

        self.info(
            "Assert walk_dirs returns only all dirs with respect of recursive as {}".format(
                recursive
            )
        )
        dirs = [
            dir_ for dir_ in j.sals.fs.walk_dirs(random_dir_dest, recursive)
        ]

        self.assertIn(random_dir_dest_2, dirs)
        if recursive:
            self.assertEqual(2, len(dirs))
            self.assertIn(random_dir_dest_3, dirs)
        else:
            self.assertEqual(1, len(dirs))
            self.assertNotIn(random_dir_dest_3, dirs)
