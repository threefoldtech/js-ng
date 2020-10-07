import string
from random import randint
from time import sleep

from jumpscale.loader import j
from parameterized import parameterized
from tests.base_tests import BaseTests

HOST = "127.0.0.1"


class RedisTests(BaseTests):
    def setUp(self):
        self.redis_instance_name = self.randstr()
        self.redis_working_dir = "/tmp/redis"

    def tearDown(self):
        self.redis_client.flushall()
        self.cmd.stop(wait_for_stop=False)
        j.tools.startupcmd.delete(self.redis_instance_name)
        j.clients.redis.delete(self.redis_instance_name)
        j.sals.fs.rmtree(self.redis_working_dir)

    def randstr(self):
        return j.data.idgenerator.nfromchoices(10, string.ascii_letters)

    def start_redis_server(self, port, password=""):
        redis_config_path = j.sals.fs.join_paths(j.sals.fs.parent(__file__), "redis.conf")
        redis_config = j.sals.fs.read_file(redis_config_path)
        redis_config = redis_config.replace("port 6379", f"port {port}")
        if password:
            redis_config = redis_config.replace("# requirepass foobared", f"requirepass {password}")
        j.sals.fs.mkdir(self.redis_working_dir)
        j.sals.fs.touch(j.sals.fs.join_paths(self.redis_working_dir, "redis.log"))
        redis_config_target_path = j.sals.fs.join_paths(self.redis_working_dir, "redis.conf")
        j.sals.fs.write_file(redis_config_target_path, redis_config)
        cmd = f"redis-server {redis_config_target_path}"
        self.cmd = j.tools.startupcmd.get(self.redis_instance_name)
        self.cmd.start_cmd = cmd
        self.cmd.ports = [port]
        self.cmd.start()

    @parameterized.expand([(False,), (True,)])
    def test01_get_redis_client(self, password):
        """Test case for getting redis client with/without password.

        **Test scenario**
        #. Start redis server with/without password.
        #. Get client for redis.
        #. Try to set and get a random variable.
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
            self.redis_client = j.clients.redis.get(self.redis_instance_name, port=port, password=passwd)
        else:
            self.redis_client = j.clients.redis.get(self.redis_instance_name, port=port)

        self.info("Try to set and get a random variable.")
        key = self.randstr()
        value = self.randstr()
        self.redis_client.set(key, value)
        result = self.redis_client.get(key)
        self.assertEqual(result.decode(), value)

    def test_02_is_running(self):
        """Test case for Checking redis is running

        **Test scenario**
        #. Get redis client before starting the server.
        #. Check that redis server is not running.
        #. Start redis server.
        #. Get client for redis.
        #. Check that the redis server is running.
        """
        self.info("Get redis client before starting the server.")
        port = randint(1000, 2000)
        self.redis_client = j.clients.redis.get(self.redis_instance_name, port=port)

        self.info("Check that redis server is not running.")
        self.assertFalse(self.redis_client.is_running())

        self.info("Start redis server.")
        self.start_redis_server(port=port)
        self.assertTrue(j.sals.nettools.wait_connection_test(HOST, port, 2))

        self.info("Get client for redis.")
        self.redis_client = j.clients.redis.get(self.redis_instance_name, port=port)

        self.info("Check that the redis server is running.")
        self.assertTrue(self.redis_client.is_running())
