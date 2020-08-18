from random import randint
from jumpscale.loader import j
from tests.base_tests import BaseTests


class TestDockerClient(BaseTests):
    DOCKER_CLIENT_NAME = "DOCKER_{}".format(randint(100, 10000))
    DOCKER_IMAGE = "threefoldtech/js-ng"

    @classmethod
    def setUpClass(cls):
        cls.client = j.clients.docker.get(cls.DOCKER_CLIENT_NAME)

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
        j.clients.docker.delete(cls.DOCKER_CLIENT_NAME)

    def docker_check_status(self, docker_name, status):
        """
        Function to check docker status, if it's running or not.
        Returns: True if the status is correct, and False otherwise.
        """
        output, error = self.os_command("docker inspect {} | grep \"Running\"".format(docker_name))
        if "\"Running\": {}".format(status) in output:
            return True
        else:
            return False

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
        self.assertIn(docker.short_id, output)

        self.info("Try to get a container with a non valid name, and make sure that it raises an error")
        with self.assertRaises(Exception) as error:
            self.client.get("test_docker_{}".format(randint(100, 1000)))
            self.assertTrue("No such container" in error.exception.args[0])

    def test02_docker_list(self):
        """
        Test list docker.

        **Test scenario**
        #. Create the first docker.
        #. Check that the docker is created correctly.
        #. Get container ID using container name.
        #. Create the second docker.
        #. Try to list this container using list subcommand with option all=False to list only the running container.
        #. Check the output of list command.
        #. Use list subcommand with option all=True to list all containers.
        #. Check the output of list command and make sure that it lists the two containers.
        """
        self.info("Check that the docker is created correctly")
        self.assertTrue(self.docker_check_status(self.DOCKER_NAME, "true"))

        self.info("Get container ID using container name")
        DOCKER_ID_1 = self.client.get(self.DOCKER_NAME).short_id

        self.info("Create second container")
        DOCKER_NAME_2 = "docker_{}".format(randint(100, 10000))
        DOCKER_ID_2 = self.client.create(DOCKER_NAME_2, self.DOCKER_IMAGE).short_id
        self.assertTrue(self.docker_check_status(DOCKER_NAME_2, "false"))

        self.info("Try to list container using list method with option all=False to list only the running container")
        docker_list = self.client.list(all=False)

        self.info("Check the output of list command")
        self.info(" it should contain the first docker, but doesn't contain the second one")
        self.assertIn(DOCKER_ID_1, str(docker_list))
        self.assertNotIn(DOCKER_ID_2, str(docker_list))

        self.info("Use list subcommand with option all=True to list all containers")
        self.info("Check the output of list command and make sure that it lists the two containers")
        docker_list = self.client.list(all=True)
        self.assertIn(DOCKER_ID_1 and DOCKER_ID_2, str(docker_list), "{} and {} isn't in the docker list"
                      .format(DOCKER_NAME_2, self.DOCKER_NAME))

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

        self.info("Use start method to start the docker")
        self.assertTrue(self.client.start(DOCKER_NAME))

        self.info("Check that docker is started correctly")
        self.assertTrue(self.docker_check_status(DOCKER_NAME, "true"))

        self.info("Use start method to start docker with non exist name, should raise an error")
        with self.assertRaises(Exception) as error:
            self.client.start(randint(1, 1000))
            self.assertIn("No such container", error.exception.args[0])

    def test04_docker_stop(self):
        """
        Test start docker.

        **Test scenario**
        #. Create docker container.
        #. Check that the docker is running.
        #. Use stop method to stop docker container.
        #. Check that docker is stopped correctly.
        #. Use stop method to stop docker with non exist name, should raise an error.
        """
        self.info("Check that the docker is running")
        self.assertTrue(self.docker_check_status(self.DOCKER_NAME, "true"))

        self.info("Use stop method to stop docker container")
        self.assertTrue(self.client.stop(self.DOCKER_NAME))

        self.info("Check that docker is stopped correctly")
        self.assertTrue(self.docker_check_status(self.DOCKER_NAME, "false"))

        self.info("Use start method to start docker with non exist name, should raise an error")
        with self.assertRaises(Exception) as error:
            self.client.stop(randint(1, 1000))
            self.assertIn("No such container", error.exception.args[0])

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
        self.assertIn("test_exec", output)

    def test06_docker_delete(self):
        """
        Test delete docker.

        **Test scenario**
        #. Create a docker container.
        #. Check that the docker has been created and it's running correctly.
        #. Use delete method to delete the container, with option force=True to delete the running container.
        #. Check that the container has been deleted correctly.
        #. Create a stopped container.
        #. Check that the docker has been created correctly and it's a stopped docker.
        #. Try to delete the stopped docker using force=False should be deleted correctly.
        #. Check that the container has been deleted correctly.
        #. Create a running container.
        #. Check that the container has been created and it's running correctly.
        #. Try to delete the running docker using force=False option it should raise an error.
        """
        self.info("Check that the container has been created and it's running correctly")
        self.assertTrue(self.docker_check_status(self.DOCKER_NAME, "true"))

        self.info("Use delete method to delete the container, with option force=True to delete the running container")
        self.assertTrue(self.client.delete(self.DOCKER_NAME, force=True))

        self.info("Check that the container has been deleted correctly")
        output, error = self.os_command("docker ps -a | grep -w \"{}\"".format(self.DOCKER_NAME))
        self.assertFalse(output)

        self.info("Create a stopped container")
        DOCKER_NAME = "DOCKER_{}".format(randint(101, 1000))
        self.client.create(DOCKER_NAME, self.DOCKER_IMAGE)

        self.info("Check that the docker has been created correctly and it's a stopped docker")
        self.assertTrue(self.docker_check_status(DOCKER_NAME, "false"))

        self.info("Try to delete the stopped docker using force=False should be deleted correctly")
        self.assertTrue(self.client.delete(DOCKER_NAME, force=False))

        self.info("Check that the container has been deleted correctly")
        output, error = self.os_command("docker ps -a | grep -w \"{}\"".format(DOCKER_NAME))
        self.assertFalse(output)

        self.info("Create a running container")
        DOCKER_NAME = "DOCKER_{}".format(randint(101, 1000))
        self.client.run(DOCKER_NAME, self.DOCKER_IMAGE)

        self.info("Check that the container has been created and it's running correctly")
        self.assertTrue(self.docker_check_status(DOCKER_NAME, "true"))

        self.info("Try to delete the running docker using force=False option it should raise an error")
        with self.assertRaises(Exception) as error:
            self.client.delete(DOCKER_NAME, force=False)
            self.assertIn("Stop the container before attempting removal or force remove", error.exception.args[0])

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
        self.assertTrue(self.docker_check_status(DOCKER_NAME, "true"))

        self.info("Check the environmental variable is created correctly")
        output, error = self.os_command("docker exec {} printenv | grep TEST".format(DOCKER_NAME))
        self.assertIn("TEST=test", output)

        self.info("Check that the hostname has been created correctly")
        output, error = self.os_command("docker exec {} hostname".format(DOCKER_NAME))
        self.assertIn("test_jsng", output)

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
        self.assertTrue(self.docker_check_status(DOCKER_NAME, "false"))
