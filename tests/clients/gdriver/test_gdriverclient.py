"""
mail: jsng2019@gmail.com
passwd: jsng123456
api_key: AIzaSyAKjjo-g1rXGEkbjA_TcP8_EsHRu7SvWls

"""
from jumpscale.god import j
from tests.base_tests import BaseTests


class GDriverClientTest(BaseTests):
    def setUp(self):
        super().setUp()
        self.client_name = self.generate_random_text()
        self.info('Create random Gdriver name : '.format(self.client_name))
        self.client = j.cients.gdrive.new(self.client_name)
        self.info("Set it's credential file ")
        self.client.credfile = "credential.json"

    def test001_github_client_get_access(self):
        self.assertEqual(j.clients.github.tft.get_userdata()['emails'][0]['email'], self.email)

