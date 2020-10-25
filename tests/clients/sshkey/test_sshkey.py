import string

from jumpscale.loader import j
from tests.base_tests import BaseTests


class SshKeyTests(BaseTests):
    def setUp(self):
        super().setUp()
        self.instance_name = self.random_name()
        self.private_key_file_name = self.random_name()
        self.sshkey_dir = f"/tmp/{self.random_name()}"

        j.sals.fs.mkdir(self.sshkey_dir)
        self.ssh_cl = j.clients.sshkey.get(name=self.instance_name)
        self.ssh_cl.private_key_path = f"{self.sshkey_dir}/{self.private_key_file_name}"

    def tearDown(self):
        j.clients.sshkey.delete(self.instance_name)
        j.sals.fs.rmtree(path=self.sshkey_dir)

    def random_name(self):
        return j.data.idgenerator.nfromchoices(10, string.ascii_letters)

    def test01_check_public_path(self):
        """Test case for checking sshkey public path.

        **Test Scenario**
        - Get a sshkey.
        - Check sshkey public path.
        """
        self.info("Check sshkey public path")
        self.assertEqual(f"{self.sshkey_dir}/{self.private_key_file_name}.pub", self.ssh_cl.public_key_path)

    def test02_check_generate_keys(self):
        """Test case for checking generate keys.

        **Test Scenario**
        - Get a sshkey.
        - Generate keys.
        - Check difference between public and private key.
        """
        self.info("Generate keys")
        self.ssh_cl.generate_keys()

        self.info("Check difference between public and private key")
        res = j.sals.process.execute(
            f'diff <( ssh-keygen -y -e -f "{self.private_key_file_name}" ) <( ssh-keygen -y -e -f "{self.private_key_file_name}.pub" )',
            cwd=self.sshkey_dir,
        )
        self.assertEqual(res[0], 0)

    def test03_check_generate_keys_with_wrong_path(self):
        """Test case for checking generate keys with wrong private key path.

        **Test Scenario**
        - Get a sshkey.
        - Set private key to wrong path.
        - Try to generate keys with wrong path it should raise an error.
        """
        wrong_path = self.random_name()
        self.info("Set private key to wrong path")
        self.ssh_cl.private_key_path = f"/te/{wrong_path}"
        self.info("Try to generate keys with wrong path it should raise an error")
        with self.assertRaises(Exception):
            self.ssh_cl.generate_keys()

    def test04_check_write_to_filesystem(self):
        """Test case for checking write keys to file system.

        **Test Scenario**
        - Get a sshkey.
        - Generate keys.
        - Set private key path.
        - Writing keys to file system.
        - Checking that keys has been written.
        """
        self.info("Generate keys")
        self.ssh_cl.generate_keys()

        self.info("Set private key path")
        dir_path = f"{self.sshkey_dir}/{self.random_name()}"
        key_file_name = self.random_name()
        j.sals.fs.mkdir(dir_path)
        self.ssh_cl.private_key_path = f"{dir_path}/{key_file_name}"

        self.info("Writing keys to file system")
        self.ssh_cl.write_to_filesystem()

        self.info("Checking that keys has been written")
        self.assertEqual(j.sals.fs.is_file(f"{dir_path}/{key_file_name}"), True)
        self.assertEqual(j.sals.fs.is_file(f"{dir_path}/{key_file_name}.pub"), True)

        self.assertEqual(self.ssh_cl.private_key, j.sals.fs.read_file(f"{dir_path}/{key_file_name}"))
        self.assertEqual(self.ssh_cl.public_key, j.sals.fs.read_file(f"{dir_path}/{key_file_name}.pub"))

    def test05_load_from_filesystem(self):
        """Test case for checking load keys from file system.

        **Test Scenario**
        - Get a sshkey.
        - Generate keys.
        - Create a new sshkey.
        - Loading keys from file system.
        - Checking that keys has been loaded.
        """
        self.info("Generate keys.")
        self.ssh_cl.generate_keys()

        self.info("Create a new sshkey")
        instance_name = self.random_name()
        ssh_cl = j.clients.sshkey.get(name=instance_name)
        ssh_cl.private_key_path = self.ssh_cl.private_key_path

        self.info("Loading keys from file system")
        ssh_cl.load_from_file_system()

        self.info("Checking that keys has been loaded")
        self.assertEqual(ssh_cl.private_key, self.ssh_cl.private_key)
        self.assertEqual(ssh_cl.public_key, self.ssh_cl.public_key)
