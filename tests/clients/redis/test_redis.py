import string
from random import randint
from time import sleep

from jumpscale.loader import j
from parameterized import parameterized
from tests.base_tests import BaseTests

HOST = "127.0.0.1"


class RedisTests(BaseTests):
    def tearDown(self):
        self.redis_client.flushall()
        self.cmd.stop(wait_for_stop=False)
        j.tools.startupcmd.delete("test_redis")
        j.clients.redis.delete("test_redis")
        j.sals.fs.rmtree("/tmp/redis.conf")

    def randstr(self):
        return j.data.idgenerator.nfromchoices(10, string.ascii_letters)

    def start_redis_server(self, port, password=""):
        passwd = ""
        if password:
            passwd = f"sed -i 's/# requirepass foobared/requirepass {password}/g' /tmp/redis.conf"
        cmd = f"""cp /etc/redis/redis.conf /tmp
            sed -i 's/port 6379/port {port}/g' /tmp/redis.conf
            {passwd}
            redis-server /tmp/redis.conf
        """
        self.cmd = j.tools.startupcmd.get("test_redis")
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
        port = randint(1000, 2000)
        if password:
            self.start_redis_server(port=port, password=passwd)
        else:
            self.start_redis_server(port=port)
        self.assertTrue(j.sals.nettools.wait_connection_test(HOST, port, 2))

        self.info("Get client for redis.")
        if password:
            self.redis_client = j.clients.redis.get("test_redis", port=port, password=passwd)
        else:
            self.redis_client = j.clients.redis.get("test_redis", port=port)

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
        port = randint(1000, 2000)
        self.redis_client = j.clients.redis.get("test_redis", port=port)

        self.info("Check that redis server is not running.")
        self.assertFalse(self.redis_client.is_running())

        self.info("Start redis server.")
        self.start_redis_server(port=port)
        self.assertTrue(j.sals.nettools.wait_connection_test(HOST, port, 2))

        self.info("Get client for redis.")
        self.redis_client = j.clients.redis.get("test_redis", port=port)

        self.info("Check that the redis server is running.")
        self.assertTrue(self.redis_client.is_running())
