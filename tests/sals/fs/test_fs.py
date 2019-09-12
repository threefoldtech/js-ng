from tests.base_tests import BaseTests
from jumpscale.god import j
from unittest import skip


class TestFS(BaseTests):
    def test001_is_ascii_file(self):
        pass

    def test002_is_empty_dir_with_empty_folder(self):
        random_dir = self.generate_random_text()
        self.info('Create /tmp/{} dir'.format(random_dir))
        j.sals.fs.mkdirs('/tmp/{}'.format(random_dir))
        self.info('Assert it is empty')
        self.assertTrue(j.sals.fs.is_empty_dir('/tmp/{}'.format(random_dir)))

    def test003_is_empty_dir_with_data(self):
        self.info('Assert /root is not empty')
        self.assertFalse(j.sals.fs.is_empty_dir('/'))

    def test004_is_empty_dir_with_file(self):
        self.info('Assert is_empty_dir with /etc/passwd raises error')
        with self.assertRaises(NotADirectoryError) as e:
            j.sals.fs.is_empty_dir('/etc/passwd')

    @skip('https://github.com/js-next/js-ng/issues/117')
    def test003_rm_tree(self):
        random_dir_1 = self.generate_random_text()
        random_dir_2 = self.generate_random_text()
        random_file = self.generate_random_text()
        self.info('Create /tmp/{}/{} dir'.format(random_dir_1, random_dir_2))
        j.sals.fs.mkdirs('/tmp/{}/{}'.format(random_dir_1, random_dir_2))

        self.info('Create random file /tmp/{}/{}'.format(random_dir_1, random_file))
        j.sals.fs.touch('/tmp/{}/{}'.format(random_dir_1, random_file))

        self.info('Remove the tree /tmp/{}'.format(random_dir_1))
        j.sals.fs.rmtree('/tmp/{}'.format(random_dir_1))

        self.info('Assert that the dir and the file have been deleted')
        self.assertTrue(j.sals.fs.is_empty_dir('/tmp/{}'.format(random_dir_1)))

    def test004_copy_stat(self):
        pass

    def test005_copy_file(self):
        random_dir_1 = self.generate_random_text()
        random_dir_2 = self.generate_random_text()
        random_file = self.generate_random_text()
        self.info('Create /tmp/{}/{} dir'.format(random_dir_1, random_dir_2))
        j.sals.fs.mkdirs('/tmp/{}/{}'.format(random_dir_1, random_dir_2))

        self.info('Create random file /tmp/{}/{}'.format(random_dir_1, random_file))
        j.sals.fs.touch('/tmp/{}/{}'.format(random_dir_1, random_file))

        src = '/tmp/{}/{}'.format(random_dir_1, random_file)
        dest = '/tmp/{}/{}/{}'.format(random_dir_1, random_dir_2, random_file)
        self.info('Copy {} to {}'.format(src, dest))
        j.sals.fs.copy_file(src, dest)

        self.info('Assert that file has been copied')
        self.assertTrue(j.sals.fs.is_file(src))
        self.assertTrue(j.sals.fs.is_file(dest))

    def test006_extension(self):
        random_file_name = '{}.py'.format(self.generate_random_text())
        dest = '/tmp/{}'.format(random_file_name)

        self.info('Create random file {}'.format(dest))
        j.sals.fs.touch(dest)

        self.info('Assert extension of file is correct')
        self.assertEqual(j.sals.fs.extension(dest), '.py')
        self.assertEqual(j.sals.fs.extension(dest, False), 'py')

    def test007_walk(self):
        random_dir_dest = '/tmp/{}'.format(self.generate_random_text())
        self.info('Create 10 files under {}'.format(random_dir_dest))
        random_files = []
        for _ in range(10):
            random_file = '{}/{}'.format(random_dir_dest, self.generate_random_text())
            j.sals.fs.touch(random_file)
            random_files.append(random_file)

        self.info('Assert walk with j.sals.fs.is_file as a filter works well')
        files = [file for file in j.sals.fs.walk(random_dir_dest, filter_fun=j.sals.fs.is_file)]
        for file in random_files:
            self.assertIn(file, files)

    def test008_walk_with_recursive(self):
        random_dir_dest = '/tmp/{}'.format(self.generate_random_text())
        random_dir_dest_2 = '{}/{}'.format(random_dir_dest, self.generate_random_text())
        self.info('Create 10 files')
        random_files = []
        for _ in range(5):
            random_file = '{}/{}'.format(random_dir_dest, self.generate_random_text())
            j.sals.fs.touch(random_file)
            random_files.append(random_file)

        for _ in range(5):
            random_file = '{}/{}'.format(random_dir_dest_2, self.generate_random_text())
            j.sals.fs.touch(random_file)
            random_files.append(random_file)

        self.info('Assert walk with j.sals.fs.is_file as a filter works well')
        files = [file for file in j.sals.fs.walk(random_dir_dest, filter_fun=j.sals.fs.is_file)]
        for file in random_files:
            self.assertIn(file, files)

    def test008_walk_non_recursive(self):
        pass

    def test009_walk_files(self):
        pass

    def test010_walk_dirs(self):
        pass

