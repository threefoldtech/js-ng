import string

from jumpscale.loader import j
from tests.base_tests import BaseTests


class GitTests(BaseTests):

    def setUp(self):
        super().setUp()
        self.instance_name = self.generate_random_text()
        self.git = j.clients.git.new(self.instance_name)
        #self.git.remote_url = 

    def tearDown(self):
        pass

    def test01_check_branch(self):
        pass
