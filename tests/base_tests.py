from unittest import TestCase

from jumpscale.loader import j
import string


class BaseTests(TestCase):
    def setUp(self):
        print("\t")
        self.info("Test case : {}".format(self._testMethodName))

    def tearDown(self):
        pass

    @staticmethod
    def generate_random_text():
        return j.data.idgenerator.chars(10)

    def random_name(self):
        return j.data.idgenerator.nfromchoices(10, string.ascii_letters)

    def info(self, message):
        j.logger.info(message)
