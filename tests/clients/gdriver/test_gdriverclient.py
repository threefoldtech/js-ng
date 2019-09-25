"""
mail: jsng2019@gmail.com
passwd: jsng123456
api_key:

"""
from jumpscale.god import j
from tests.base_tests import BaseTests


class GDriverClientTest(BaseTests):
    def setUp(self):
        super().setUp()
        self.client_name = self.generate_random_text()
        self.info('Create random Gdriver name : '.format(self.client_name))
        self.client = j.clients.gdrive.new(self.client_name)
        self.info("Set it's credential file ")
        self.client.credfile = "/{}/credential.json".format(j.sals.fs.cwd())



