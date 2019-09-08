from unittest import TestCase
from loguru import logger
from uuid import uuid4


class BaseTests(TestCase):
    LOGGER = logger

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @staticmethod
    def generate_random_text():
        return str(uuid4()).replace("-", "")[:10]

    def info(self, message):
        BaseTests.LOGGER.info(message)
