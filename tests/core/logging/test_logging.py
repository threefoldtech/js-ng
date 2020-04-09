import unittest
from jumpscale.god import j


class TestLogging(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.appname = "test"
        j.core.application.start("test")

    def setUp(self):
        j.core.logging.redis.remove_all_records(self.appname)

    def tearDown(self):
        j.core.logging.redis.remove_all_records(self.appname)

    def test01_redis_handler(self):
        test_records_count = j.core.logging.redis.max_size * 3

        for i in range(test_records_count):
            j.core.logging.logger.info("message {}", i + 1)

        records_count = j.core.logging.redis.records_count(self.appname)
        self.assertEqual(records_count, test_records_count)

        for i in range(records_count):
            record_id = i + 1
            record = j.core.logging.redis.record_get(record_id, self.appname)
            self.assertEqual(record["id"], record_id)
