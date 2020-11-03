from tests.base_tests import BaseTests
from jumpscale.loader import j

REDIS_PORT = 6379
TEST_APP_NAME = "test"


class TestLogging(BaseTests):
    @classmethod
    def setUpClass(cls):
        cls.cmd = None
        cls.messages = []
        if not j.sals.nettools.tcp_connection_test("127.0.0.1", REDIS_PORT, 1):
            cls.cmd = j.tools.startupcmd.get("test_logging")
            cls.cmd.start_cmd = "redis-server"
            cls.cmd.ports = [REDIS_PORT]
            cls.cmd.start()

        j.logger.register(TEST_APP_NAME)
        # limit max_size for testing
        j.logger.redis._max_size = 100

    def setUp(self):
        j.logger.redis.remove_all_records(TEST_APP_NAME)

    def tearDown(self):
        j.logger.redis.remove_all_records(TEST_APP_NAME)

    @classmethod
    def tearDownClass(cls):
        j.logger.unregister()
        if cls.cmd:
            cls.cmd.stop(wait_for_stop=False)
            j.tools.startupcmd.delete("test_logging")

    def handler(self, message):
        if "CRITICAL" in message:
            level = "CRITICAL"
        elif "ERROR" in message:
            level = "ERROR"
        elif "WARNING" in message:
            level = "WARNING"
        elif "INFO" in message:
            level = "INFO"
        elif "DEBUG" in message:
            level = "DEBUG"
        else:
            level = None

        msg = message[message.find("-", message.find(__name__)) + 2 :].strip()
        log = {"message": msg, "level": level}
        self.messages.append(log)

    def test01_redis_handler(self):
        test_records_count = j.logger.redis.max_size * 2

        for i in range(test_records_count):
            test_value = i + 1
            j.logger.info("message {}", test_value, category=str(test_value), data={"key": test_value})

        records_count = j.logger.redis.records_count(TEST_APP_NAME)
        self.assertEqual(records_count, test_records_count)

        for i in range(records_count):
            test_value = i + 1
            record = j.logger.redis.record_get(test_value, TEST_APP_NAME)
            self.assertEqual(record["id"], test_value)
            self.assertEqual(record["category"], str(test_value))
            self.assertEqual(record["data"]["key"], test_value)

        records = j.logger.redis.tail(TEST_APP_NAME, limit=10)
        self.assertEqual(len(list(records)), 10)

        records = j.logger.redis.tail(TEST_APP_NAME)
        self.assertEqual(len(list(records)), j.logger.redis.max_size)

    def test_02_test_log_level(self):
        j.logger.add_handler(self.handler)
        levels = ["critical", "error", "exception", "warning", "info", "debug"]
        for level in levels:
            msg = self.generate_random_text()
            log = getattr(j.logger, level)
            log(msg)
            message = self.messages.pop()
            self.assertEqual(message["message"], msg)
            if level == "exception":
                self.assertEqual(message["level"], "ERROR")
            else:
                self.assertEqual(message["level"], level.upper())

    def test_03_test_register_invalid_app_name(self):
        with self.assertRaises(j.exceptions.Value):
            j.logger.register("")
