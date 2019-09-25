from unittest import skip
from jumpscale.god import j
from tests.base_tests import BaseTests


class TestTmux(BaseTests):
    def test001_create_session(self):
        session_name = self.generate_random_text()
        self.info("Create session with name : {}".format(session_name))
        session = j.core.executors.tmux.create_session(session_name)
        self.assertIn(session_name, str(j.core.executors.tmux.server.sessions[0]))
        self.info('Kill session')
        session.kill_session()

    def test002_create_existing_session(self):
        session_name = self.generate_random_text()
        self.info("Create session with name : {}".format(session_name))
        session = j.core.executors.tmux.create_session(session_name)
        with self.assertRaises(Exception):
            j.core.executors.tmux.create_session(session_name)
        self.assertIn(session_name, str(j.core.executors.tmux.server.sessions[0]))
        self.info('Kill session')
        session.kill_session()

    def test003_get_js_session(self):
        self.info("Get js session, should pass")
        self.assertIn(j.core.executors.tmux.JS_SESSION_NAME, str(j.core.executors.tmux.get_js_session()))

    def test004_get_js_window(self):
        self.assertIn(j.core.executors.tmux.JS_WINDOW_NAME, str(j.core.executors.tmux.get_js_window()))
