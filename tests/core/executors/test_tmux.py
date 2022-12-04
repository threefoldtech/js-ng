from unittest import skip

from jumpscale.loader import j
from libtmux.exc import LibTmuxException
from tests.base_tests import BaseTests


class TestTmux(BaseTests):
    def setUp(self):
        self.session_to_clear = []
        self.window_to_clear = []

    def test001_create_session(self):
        session_name = self.generate_random_text()
        self.info("Create session with name : {}".format(session_name))
        session = j.core.executors.tmux.create_session(session_name)
        self.session_to_clear.append(session)

        self.assertIn(session_name, str(j.core.executors.tmux.server.sessions))

    def test002_create_existing_session(self):
        session_name = self.generate_random_text()
        self.info("Create session with name : {}".format(session_name))
        session = j.core.executors.tmux.create_session(session_name)
        self.session_to_clear.append(session)

        with self.assertRaises(LibTmuxException):
            j.core.executors.tmux.create_session(session_name)

        self.assertIn(session_name, str(j.core.executors.tmux.server.sessions))

    def test003_get_js_session(self):
        self.info("Get js session, should pass")
        session = j.core.executors.tmux.get_js_session()
        self.assertIn(j.core.executors.tmux.JS_SESSION_NAME, str(session))

    def test004_get_js_window(self):
        window_name = self.generate_random_text()
        self.info("Create window with name : {}".format(window_name))
        window = j.core.executors.tmux.get_js_window(window_name)
        self.window_to_clear.append(window)

        session = j.core.executors.tmux.get_js_session()
        self.assertIn(window_name, str(session.windows))

    def test005_execute_in_window(self):
        cmd = "python3 -m http.server 1234"
        window_name = self.generate_random_text()
        j.core.executors.tmux.execute_in_window(cmd, window_name)
        self.assertTrue(
            j.sals.nettools.wait_connection_test("127.0.0.1", 1234, 2)
        )
        window = j.core.executors.tmux.get_js_window(window_name)
        self.window_to_clear.append(window)

    def tearDown(self):
        for session in self.session_to_clear:
            j.core.executors.tmux.kill_session(session.name)
        for window in self.window_to_clear:
            window.kill_window()
