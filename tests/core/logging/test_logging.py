import unittest
from jumpscale.god import j


class TestLogging(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        j.application.start("test")

    def setUp(self):
        j.logger.redis.remove_all_records(j.application.appname)

    def tearDown(self):
        j.logger.redis.remove_all_records(j.application.appname)

    def test01_redis_handler(self):
        test_records_count = j.logger.redis.max_size * 2

        for i in range(test_records_count):
            test_value = i + 1
            j.logger.info("message {}", test_value, category=str(test_value), data={"key": test_value})

        records_count = j.logger.redis.records_count(j.application.appname)
        self.assertEqual(records_count, test_records_count)

        for i in range(records_count):
            test_value = i + 1
            record = j.logger.redis.record_get(test_value, j.application.appname)
            self.assertEqual(record["id"], test_value)
            self.assertEqual(record["category"], str(test_value))
            self.assertEqual(record["data"]["key"], test_value)

        records = j.logger.redis.tail(j.application.appname, limit=10)
        self.assertEqual(len(list(records)), 10)

        records = j.logger.redis.tail(j.application.appname)
        self.assertEqual(len(list(records)), j.logger.redis.max_size)
