from random import randint
from jumpscale.loader import j
from base_test import BaseTest


class TestDockerClient(BaseTest):
    DOCKER_CLIENT = "DOCKER_{}".format(randint(100, 10000))
    DOCKER_IMAGE = "threefoldtech/js-ng"

    @classmethod
    def setUpClass(cls):

        cls.client = j.clients.docker.get(cls.DOCKER_CLIENT)

    def setUp(self):
        print("\t")
        self.info("Test case : {}".format(self._testMethodName))

        self.info("Create docker using jsng")
        self.DOCKER_NAME = "docker_{}".format(randint(1, 100))
        self.client.run(self.DOCKER_NAME, self.DOCKER_IMAGE)

    def tearDown(self):
        self.info("Remove all dockers which start with docker or DOCKER")
        self.os_command("docker rm -f $(docker ps -aqf \"name=docker|DOCKER\")")

    @classmethod
    def tearDownClass(cls):
        cls.info("Remove Docker client")
        j.clients.docker.delete(cls.DOCKER_CLIENT)

    def test01_docker_get(self):
        """
        Test getting container.

        **Test scenario**
        #. Create docker container.
        #. Get container ID using container name.
        #. Try to get this container one time using container name.
        #. Try to get a container with a non valid name, and make sure that it raises an error.
        """
        self.info("Get container ID using container name")
        output, error = self.os_command("docker ps -aqf name={}".format(self.DOCKER_NAME))
        self.assertTrue(output)

        self.info("Try to get this container one time using container name")

        docker = self.client.get(self.DOCKER_NAME)
        self.assertIn(docker.short_id, output.decode())

        self.info("Try to get a container with a non valid name, and make sure that it raises an error")
        with self.assertRaises(Exception) as error:
            self.client.get("test_docker").format(randint(1, 1000))
            self.assertTrue("No such container" in error.exception.args[0])

    def test02_docker_list(self):
        """
        Test list docker.

        **Test scenario**
        #. Create docker container.
        #. Get container ID using container name.
        #. Try to list this container using list subcommand with option all=False to list only the running container.
        #. Check the output of list command.
        #. Create second container.
        #. Use list subcommand with option all=True to list all containers.
        #. Check the output of list command and make sure that it lists the two containers.
        """

        self.info("Get container ID using container name")
        output, error = self.os_command("docker ps -qf name={}".format(self.DOCKER_NAME))
        self.assertTrue(output)

        self.info("Try to list this container using list subcommand with option all=False to list only the running \
        container")
        docker_list = self.client.list(all=False)

        self.info("Check the output of list command")
        for i in range(len(docker_list)):
            if docker_list[i].short_id in output.decode():
                self.assertTrue(True)

        self.info("Create second container")
        DOCKER_NAME_2 = "docker_{}".format(randint(100, 10000))
        DOCKER_ID_2 = self.client.create(DOCKER_NAME_2, self.DOCKER_IMAGE).short_id

        self.info("Use list subcommand with option all=True to list all containers")
        self.info("Check the output of list command and make sure that it lists the two containers")
        docker_list = self.client.list(all=True)
        output, error = self.os_command("docker ps -qaf \"name=docker|DOCKER\"")
        for i in range(len(docker_list)):
            if docker_list[i].short_id in output.decode():
                DOCKER_ID_1 = docker_list[i].short_id
                self.assertIn(DOCKER_ID_1, output.decode())
            elif docker_list[i].short_id == DOCKER_ID_2:
                self.assertIn(DOCKER_ID_2, output.decode())

    def test03_docker_start(self):
        """
        Test start docker.

        **Test scenario**
        #. Create docker container.
        #. Use start method to start docker container.
        #. Check that docker is started correctly.
        #. Use start method to start docker with non exist name, should raise an error.
        """
        self.info("Create docker container")
        DOCKER_NAME = "docker_{}".format(randint(100, 10000))
        self.client.create(DOCKER_NAME, self.DOCKER_IMAGE)

        self.info("Use start method to start docker container, ")
        self.assertTrue(self.client.start(DOCKER_NAME))

        self.info("Check that docker is started correctly")
        output, error = self.os_command("docker inspect {} | grep \"Running\"".format(DOCKER_NAME))
        self.assertIn("\"Running\": true", output.decode())

        self.info("Use start method to start docker with non exist name, should raise an error")
        with self.assertRaises(Exception) as error:
            self.client.start(randint(1, 1000))
            self.assertTrue("No such container" in error.exception.args[0])

    def test04_docker_stop(self):
        """
        Test start docker.

        **Test scenario**
        #. Create docker container.
        #. Use stop method to stop docker container.
        #. Check that docker is stopped correctly.
        #. Use stop method to stop docker with non exist name, should raise an error.
        """
        self.info("Use stop method to stop docker container")
        self.assertTrue(self.client.stop(self.DOCKER_NAME))

        self.info("Check that docker is stopped correctly")
        self.info("Check that docker is started correctly")
        output, error = self.os_command("docker inspect {} | grep \"Running\"".format(self.DOCKER_NAME))
        self.assertIn("\"Running\": false", output.decode())

        self.info("Use start method to start docker with non exist name, should raise an error")
        with self.assertRaises(Exception) as error:
            self.client.stop(randint(1, 1000))
            self.assertTrue("No such container" in error.exception.args[0])

    def test05_docker_exec(self):
        """
        Test exec docker.

        **Test scenario**

        #. Create a docker container.
        #. Use docker exec method to create file in /tmp.
        #. check that file has been created correctly.
        """

        self.info("Use docker exec method to create file in /tmp")
        execute_command = self.client.exec(self.DOCKER_NAME, "touch /tmp/test_exec")
        self.assertIn("exit_code=0", str(execute_command))

        self.info("check that file has been created correctly")
        output, error = self.os_command("docker exec {}  ls /tmp/".format(self.DOCKER_NAME))
        self.assertIn("test_exec", output.decode())

    def test06_docker_delete(self):
        """
        Test delete docker.

        **Test scenario**
        #. Create a docker container.
        #. Use delete method to delete the container, with option force=True to delete the running container,
           should be deleted correctly.
        #. Check that the container has been deleted correctly.
        #. Create a stopped container.
        #. Try to delete the stopped docker using force=False should be deleted correctly.
        #. Check that the container has been deleted correctly.
        #. Create a running container.
        #. Try to delete the running docker using force=False option it should raise an error.
        """

        self.info("Use delete method to delete the container, with option force=True to delete the running container, \
                   should be deleted correctly.")
        self.assertTrue(self.client.delete(self.DOCKER_NAME, force=True))

        self.info("Check that the container has been deleted correctly")
        output, error = self.os_command("docker ps -a | grep -w \"{}\"".format(self.DOCKER_NAME))
        self.assertFalse(output.decode())

        self.info("Create a stopped container")
        DOCKER_NAME = "DOCKER_{}".format(randint(101, 1000))
        self.client.create(DOCKER_NAME, self.DOCKER_IMAGE)

        self.info("Try to delete the stopped docker using force=False should be deleted correctly")
        self.assertTrue(self.client.delete(DOCKER_NAME, force=False))

        self.info("Check that the container has been deleted correctly")
        output, error = self.os_command("docker ps -a | grep -w \"{}\"".format(DOCKER_NAME))
        self.assertFalse(output.decode())

        self.info("Create a running container")
        DOCKER_NAME = "DOCKER_{}".format(randint(101, 1000))
        self.client.run(DOCKER_NAME, self.DOCKER_IMAGE)

        self.info("Try to delete the running docker using force=False option it should raise an error")
        with self.assertRaises(Exception) as error:
            self.client.delete(DOCKER_NAME, force=False)
            self.assertTrue("Stop the container before attempting removal or force remove" in error.exception.args[0])

    def test07_docker_run(self):
        """
        Test run docker.

        **Test scenario**
        #. Create a docker with run command. With those options:
            1. Add hostname using hostname option.
            2. Add environmental variable.
        #. Check that the docker has been created correctly.
        #. Check the environmental variable is created correctly.
        #. Check that the hostname has been created correctly.
        """

        self.info("Create a docker with run command")
        DOCKER_NAME = "DOCKER_{}".format(randint(150, 15000))
        self.client.run(name=DOCKER_NAME, image=self.DOCKER_IMAGE, hostname="test_jsng", environment=["TEST=test"])

        self.info("Check that the docker has been created correctly")
        output, error = self.os_command("docker inspect {} | grep \"Running\"".format(DOCKER_NAME))
        self.assertIn("\"Running\": true", output.decode())

        self.info("Check the environmental variable is created correctly")
        output, error = self.os_command("docker exec {} printenv | grep TEST".format(DOCKER_NAME))
        self.assertIn("TEST=test", output.decode())

        self.info("Check that the hostname has been created correctly")
        output, error = self.os_command("docker exec {} hostname".format(DOCKER_NAME))
        self.assertIn("test_jsng", output.decode())

    def test08_docker_create(self):
        """
        Test run docker.

        **Test scenario**
        #. Create a docker with create method.
        #. Check that docker has been create successfully.
        """
        self.info("Create a docker with create method")
        DOCKER_NAME = "DOCKER_{}".format(randint(1000, 10000))
        self.client.create(DOCKER_NAME, self.DOCKER_IMAGE)

        self.info("Check that docker has been create successfully")
        output, error = self.os_command("docker inspect {} | grep \"Running\"".format(DOCKER_NAME))
        self.assertIn("\"Running\": false", output.decode())
