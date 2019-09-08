# i created new fake github account
# email: tft.testing.19@gmail.com.
# password: tft_password19
# username: tfttesting
# name: Codescalers Test
# organization: fakeForTest2

from jumpscale.god import j
from tests.base_tests import BaseTests


class GithubClientTest(BaseTests):
    def setUp(self):
        super().setUp()
        self.username = "tfttesting"
        self.password = "tft_password19"
        self.email = "tft.testing.19@gmail.com"
        j.clients.github.new("tft")
        j.clients.github.tft.username = self.username
        j.clients.github.tft.password = self.password
        self.client = j.clients.github.tft.github_client

    def test001_github_client_get_access(self):
        self.assertEqual(j.clients.github.tft.get_userdata()['emails'][0]['email'], self.email)

