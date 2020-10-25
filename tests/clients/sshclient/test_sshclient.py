import string

from jumpscale.loader import j
from tests.base_tests import BaseTests
from os import getenv
import time


class SshClientTests(BaseTests):
    def setUp(self):
        super().setUp()

        self.info("Get a ssh key")
        self.ssh_client_name = self.random_name()
        self.sshkey_file_name = self.random_name()
        self.sshkey_dir = f"/tmp/{self.random_name()}"
        j.sals.fs.mkdir(self.sshkey_dir)

        self.ssh_cl = j.clients.sshkey.get(self.ssh_client_name)
        self.ssh_cl.private_key_path = f"{self.sshkey_dir}/{self.sshkey_file_name}"
        self.ssh_cl.generate_keys()
        pub_key = self.ssh_cl.public_key

        self.info("Get a ssh client")
        self.localclient = j.clients.sshclient.get(self.ssh_client_name)
        self.localclient.sshkey = self.ssh_client_name

        self.info("Create docker using nginx")
        self.DOCKER_CLIENT_NAME = self.random_name().lower()
        self.docker_name = self.random_name().lower()
        self.docker_image = "nginx:latest"

        self.docker_client = j.clients.docker.get(self.DOCKER_CLIENT_NAME)
        self.docker_client.run(self.docker_name, self.docker_image, environment={"pub_key": pub_key})

        self.docker_client.exec(self.docker_name, "apt-get update")
        self.docker_client.exec(self.docker_name, "apt-get install ssh -y")
        self.docker_client.exec(self.docker_name, "mkdir /root/.ssh")
        self.docker_client.exec(self.docker_name, "mkdir -p /var/run/sshd")
        self.docker_client.exec(self.docker_name, "touch /root/.ssh/authorized_keys")
        self.docker_client.exec(self.docker_name, '/bin/bash -c "echo $pub_key >> /root/.ssh/authorized_keys"')
        self.docker_client.exec(self.docker_name, "service ssh start")

        command = 'docker inspect -f "{{ .NetworkSettings.IPAddress }}" ' + self.docker_name
        docker_ip_address = j.sals.process.execute(command)
        docker_ip_address = docker_ip_address[1].rstrip("\n")
        self.localclient.host = docker_ip_address

    def tearDown(self):
        j.clients.sshkey.delete(self.ssh_client_name)
        j.sals.fs.rmtree(path=self.sshkey_dir)
        j.clients.docker.delete(self.DOCKER_CLIENT_NAME)

        self.info("Remove docker")
        j.sals.process.execute(f"docker rm -f {self.docker_name}")

    def random_name(self):
        return j.data.idgenerator.nfromchoices(10, string.ascii_letters)

    def test01_run_command(self):
        """Test case for ssh to container.

        **Test Scenario**
        - Get a sshkey.
        - Get a sshclient.
        - Create docker using nginx.
        - Check ssh to container.
        """
        self.info("Check connecting to container")
        _, res, _ = self.localclient.sshclient.run("hostname")
        self.assertAlmostEqual(res.rstrip("\n"), "js-ng")

    def test02_reset_connection(self):
        """Test case for reset connection and try to connect.

        **Test Scenario**
        - Get a sshclient.
        - Reset connection.
        - Try to connect to container should raise an error.
        """
        self.info("Reset connection")
        self.localclient.reset_connection()
        self.info("Try to connect to container")
        _, res, _ = self.localclient.sshclient.run("hostname")
        self.assertAlmostEqual(res.rstrip("\n"), "js-ng")
