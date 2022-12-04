import pytest
from jumpscale.loader import j
from tests.base_tests import BaseTests


@pytest.mark.integration
class SshClientTests(BaseTests):
    def setUp(self):
        super().setUp()

        self.info("Get a ssh key")
        self.ssh_client_name = self.random_name()
        self.sshkey_file_name = self.random_name()
        self.sshkey_dir = j.sals.fs.join_paths("/tmp", self.random_name())
        j.sals.fs.mkdir(self.sshkey_dir)

        self.ssh_cl = j.clients.sshkey.get(self.ssh_client_name)
        self.ssh_cl.private_key_path = j.sals.fs.join_paths(
            self.sshkey_dir, self.sshkey_file_name
        )
        self.ssh_cl.generate_keys()
        pub_key = self.ssh_cl.public_key

        self.info("Get a ssh client")
        self.localclient = j.clients.sshclient.get(self.ssh_client_name)
        self.localclient.sshkey = self.ssh_client_name

        self.info("Create a docker container using ubuntu image")
        self.docker_client_name = self.random_name().lower()
        self.docker_name = self.random_name().lower()
        self.docker_image = "ubuntu:latest"

        self.docker_client = j.clients.docker.get(self.docker_client_name)
        self.docker_client.run(
            self.docker_name,
            self.docker_image,
            environment={"pub_key": pub_key},
            entrypoint="tail -f /dev/null",
        )

        cmds = """
        apt-get update
        apt-get install ssh -y
        mkdir /root/.ssh
        mkdir -p /var/run/sshd
        touch /root/.ssh/authorized_keys
        echo $pub_key >> /root/.ssh/authorized_keys
        service ssh start"""

        self.docker_client.exec(self.docker_name, f"/bin/bash -c '{cmds}'")

        self.container = self.docker_client.get(self.docker_name)
        self.localclient.host = self.container.attrs["NetworkSettings"][
            "IPAddress"
        ]

    def tearDown(self):
        j.clients.sshkey.delete(self.ssh_client_name)
        j.sals.fs.rmtree(path=self.sshkey_dir)
        j.clients.docker.delete(self.docker_client_name)

        self.info("Remove docker")
        self.container.stop()
        self.docker_client.delete(self.docker_name)

    def test01_run_command(self):
        """Test case for ssh to container.

        **Test Scenario**
        - Get a sshkey.
        - Get a sshclient.
        - Create a docker container using ubuntu image.
        - Check ssh to container.
        """
        self.info("Check connecting to container")
        _, res, _ = self.localclient.sshclient.run("hostname")
        self.assertEqual(res.rstrip(), "js-ng")
