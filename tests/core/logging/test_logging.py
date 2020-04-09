import unittest
from jumpscale.core.logging import Logger
from tests.base_tests import BaseTests


class TestLocal(BaseTests):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.appname = "test"
        self.logger = Logger(appname=self.appname)

    def tearDown(self):
        self.logger.redis_handler.remove_all_records(self.appname)

    def test01_redis_handler(self):
        test_records_count = self.logger.redis_handler.max_size * 3

        for i in range(test_records_count):
            self.logger.logger.info("message", i + 1)

        records_count = self.logger.redis_handler.records_count(self.appname)
        self.assertEqual(records_count, test_records_count)

        for i in range(records_count):
            record_id = i + 1
            record = self.logger.redis_handler.get_record(record_id, self.appname)
            self.assertEqual(record["id"], record_id)
