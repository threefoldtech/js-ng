from unittest import TestCase
from loguru import logger
from uuid import uuid4
from subprocess import Popen, PIPE, STDOUT


class BaseTests(TestCase):
    LOGGER = logger

    def setUp(self):
        print("\t")
        self.info("Test case : {}".format(self._testMethodName))

    def tearDown(self):
        pass

    @staticmethod
    def generate_random_text():
        return str(uuid4()).replace("-", "")[:10]

    def info(self, message):
        BaseTests.LOGGER.info(message)

    @staticmethod
    def os_command(command):
        process = Popen(command, shell=True, stdout=PIPE, stderr=STDOUT, universal_newlines=True)
        output, error = process.communicate()
        return output, error
