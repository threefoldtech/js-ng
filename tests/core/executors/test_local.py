import io
import sys

from invoke.exceptions import UnexpectedExit
from parameterized import parameterized
from unittest import TestCase

from jumpscale.loader import j
from tests.base_tests import BaseTests

CMD_STR = "which ls"
CMD_LIST = ["which", "ls"]


class TestLocal(BaseTests):
    @parameterized.expand([(CMD_STR, True), (CMD_LIST, False)])
    def test001_execute_local_command(self, cmd, warn):
        self.info(f"Execute `{cmd}` as local command with warn {warn}")
        code, stdout, stderr = j.core.executors.run_local(cmd, warn=warn)
        self.assertEqual(0, code)
        self.assertIn("ls", stdout)
        self.assertEqual("", stderr)

    def test002_execute_wrong_local_command(self):
        self.info("Execute wrong command and assert there is an error")
        with self.assertRaises(UnexpectedExit):
            j.core.executors.run_local("random")

    def test003_execute_wrong_local_command_with_warn(self):
        _, stdout, stderr = j.core.executors.run_local("random", warn=True)
        self.assertEqual("", stdout)
        self.assertIn("random: command not found", stderr)

    @parameterized.expand([(CMD_STR, True), (CMD_LIST, False)])
    def test004_execute_local_command_with_hide(self, cmd, hide):
        self.info(f"Execute command `{cmd}` with hide {hide} and assert that sout is okay")
        capture = io.StringIO()
        sys.stdout = capture
        _, stdout, _ = j.core.executors.run_local(cmd, hide=hide)
        output = capture.getvalue()
        capture.close()
        sys.stdout = sys.__stdout__
        if hide:
            self.assertEqual(output, "")
        else:
            self.assertEqual(output, stdout)

    @parameterized.expand([(CMD_STR, True), (CMD_LIST, False)])
    def test005_execute_local_command_with_echo(self, cmd, echo):
        self.info(f"Execute command `{cmd}`with echo {echo} and assert that sout is okay")
        capture = io.StringIO()
        sys.stdout = capture
        j.core.executors.run_local(cmd, echo=echo)
        output = capture.getvalue()
        capture.close()
        sys.stdout = sys.__stdout__
        if echo:
            self.assertIn(CMD_STR, output)
        else:
            self.assertNotIn(CMD_STR, output)

    @parameterized.expand([(CMD_STR,), (CMD_LIST,)])
    def test006_execute_local_command_hide_overwrite_echo(self, cmd):
        self.info(f"Execute command `{cmd}` and assert that hide overwrites echo")
        capture = io.StringIO()
        sys.stdout = capture
        j.core.executors.run_local(cmd, echo=True, hide=True)
        output = capture.getvalue()
        capture.close()
        sys.stdout = sys.__stdout__
        self.assertEqual("", output)

    def test007_execute_local_command_with_env(self):
        self.info("Execute command and export env variable")
        _, stdout, _ = j.core.executors.run_local("echo $PATH", env={"PATH": ""})
        self.assertEqual("\n", stdout)
