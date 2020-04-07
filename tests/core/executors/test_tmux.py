from unittest import skip
from jumpscale.god import j
from tests.base_tests import BaseTests


class TestTmux(BaseTests):
    def test001_create_session(self):
        session_name = self.generate_random_text()
        self.info("Create session with name : {}".format(session_name))
        j.core.executors.tmux.create_session(session_name)
        self.assertIn(session_name, str(j.core.executors.tmux.server.sessions))

    @skip("https://github.com/js-next/js-ng/issues/111")
    def test002_create_existing_session(self):
        session_name = self.generate_random_text()
        self.info("Create session with name : {}".format(session_name))
        j.core.executors.tmux.create_session(session_name)
        j.core.executors.tmux.create_session(session_name)
        self.assertIn(session_name, str(j.core.executors.tmux.server.sessions[0]))

    @skip("https://github.com/js-next/js-ng/issues/108")
    def test003_get_js_session(self):
        self.info("Get js session, should pass")
        self.assertIn(j.core.executors.tmux.JS_SESSION_NAME, str(j.core.executors.tmux.get_js_session()))

    @skip("https://github.com/js-next/js-ng/issues/109")
    def test004_get_js_window(self):
        window_name = self.generate_random_text()
        self.info("Create window with name : {}".format(window_name))
        j.core.executors.tmux.get_js_window(window_name)
        self.assertIn(window_name, str(j.core.executors.tmux.server.windows[0]))

    @skip("https://github.com/js-next/js-ng/issues/109")
    def test005_execute_in_window(self):
        # TODO
        pass
