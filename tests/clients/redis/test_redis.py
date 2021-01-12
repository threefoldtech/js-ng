import string
from random import randint

from jumpscale.loader import j
from parameterized import parameterized
from tests.base_tests import BaseTests

HOST = "127.0.0.1"


class RedisTests(BaseTests):
    def setUp(self):
        self.redis_instance_name = self.randstr()
        self.port = randint(20000, 21000)

    def tearDown(self):
        self.redis_client.flushall()
        self.cmd.stop(wait_for_stop=False)
        j.tools.startupcmd.delete(self.redis_instance_name)
        j.clients.redis.delete(self.redis_instance_name)

    def randstr(self):
        return j.data.idgenerator.nfromchoices(10, string.ascii_letters)

    def start_redis_server(self, port, password=""):
        cmd = f"redis-server --port {self.port} --bind {HOST}"  
        if password:
            cmd += f" --requirepass {password}"
        self.cmd = j.tools.startupcmd.get(self.redis_instance_name)
        self.cmd.start_cmd = cmd
        self.cmd.ports = [port]
        self.cmd.start()

    @parameterized.expand([(False,), (True,)])
    def test01_get_redis_client(self, password):
        """Test case for getting redis client with/without password.

        **Test Scenario**

        - Start redis server with/without password.
        - Get client for redis.
        - Try to set and get a random variable.
        """
        self.info("Start redis server with/without password.")
        passwd = self.randstr()

        if password:
            self.start_redis_server(port=self.port, password=passwd)
        else:
            self.start_redis_server(port=self.port)
        self.assertTrue(j.sals.nettools.wait_connection_test(HOST, self.port, 2))

        self.info("Get client for redis.")
        if password:
            self.redis_client = j.clients.redis.get(self.redis_instance_name, port=self.port, password=passwd)
        else:
            self.redis_client = j.clients.redis.get(self.redis_instance_name, port=self.port)

        self.info("Try to set and get a random variable.")
        key = self.randstr()
        value = self.randstr()
        self.redis_client.set(key, value)
        result = self.redis_client.get(key)
        self.assertEqual(result.decode(), value)

    def test_02_is_running(self):
        """Test case for Checking redis is running.

        **Test Scenario**

        - Get redis client before starting the server.
        - Check that redis server is not running.
        - Start redis server.
        - Get client for redis.
        - Check that the redis server is running.
        """
        self.info("Get redis client before starting the server.")
        self.redis_client = j.clients.redis.get(self.redis_instance_name, port=self.port)

        self.info("Check that redis server is not running.")
        self.assertFalse(self.redis_client.is_running())

        self.info("Start redis server.")
        self.start_redis_server(port=self.port)
        self.assertTrue(j.sals.nettools.wait_connection_test(HOST, self.port, 2))

        self.info("Get client for redis.")
        self.redis_client = j.clients.redis.get(self.redis_instance_name, port=self.port)

        self.info("Check that the redis server is running.")
        self.assertTrue(self.redis_client.is_running())
