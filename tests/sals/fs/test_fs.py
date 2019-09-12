from tests.base_tests import BaseTests
from jumpscale.god import j


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

    def test003_rm_tree(self):
        random_dir_1 = self.generate_random_text()
        random_dir_2 = self.generate_random_text()
        random_file = self.generate_random_text()
        self.info('Create /tmp/{}/{} dir'.format(random_dir_1, random_dir_2))
        j.sals.fs.mkdirs('/tmp/{}/{}'.format(random_dir_1, random_dir_2))

        self.info('Create random file /tmp/{}/{}/{}'.format(random_dir_1, random_dir_2, random_file))
        j.sals.fs.touch('/tmp/{}/{}/{}'.format(random_dir_1, random_dir_2, random_file))

        self.info('Remove the tree /tmp/{}'.format(random_dir_1))
        j.sals.fs.rmtree('/tmp/{}'.format(random_dir_1))

        self.info('Assert that the dir and the file have been deleted')
        self.assertTrue(j.sals.fs.is_empty_dir('/tmp/{}'.format(random_dir_1)))

    def test004_copy_stat(self):
        pass

    def test005_copy_file(self):
        pass

    def test006_extension(self):
        pass

    def test007_walk(self):
        pass

    def test008_walk_non_recursive(self):
        pass

    def test009_walk_files(self):
        pass

    def test010_walk_dirs(self):
        pass

