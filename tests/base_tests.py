from unittest import TestCase
import string
from jumpscale.loader import j


class BaseTests(TestCase):
    def setUp(self):
        print("\t")
        self.info("Test case : {}".format(self._testMethodName))

    def tearDown(self):
        pass

    @staticmethod
    def random_name():
        return j.data.idgenerator.nfromchoices(10, string.ascii_letters)

    def info(self, message):
        j.logger.info(message)
