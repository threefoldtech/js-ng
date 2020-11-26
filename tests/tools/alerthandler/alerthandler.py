from tests.base_tests import BaseTests
from jumpscale.loader import j
from unittest import skip
from parameterized import parameterized
import time


class TestFS(BaseTests):
    def test_adding_handler(self):
        """Tests registering alert handlers"""
        self.alert = None

        def alert_handler(alert):
            self.alert = alert

        self.info("Registering handler")
        j.tools.alerthandler.register_handler(alert_handler)
        j.tools.alerthandler.alert_raise("Tests", "tests")
        for i in range(3):
            if not self.alert:
                time.sleep(5)
                continue
            self.info(f"alertid = {self.alert.id}")
            self.assertEquals(self.alert.app_name, "Tests")
            self.assertEquals(self.alert.message, "tests")
            break
        else:
            self.fail("Alert handler not registered")
