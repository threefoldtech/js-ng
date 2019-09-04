from unittest import TestCase
from jumpscale.god import j
from invoke.exceptions import UnexpectedExit
from parameterized import parameterized
import io, sys


class TestLocal(TestCase):
    @parameterized.expand([(True, ), (False, )])
    def test001_execute_local_command(self, warn):
        code, stdout, stderr = j.core.executors.run_local('which ls', warn=warn)
        self.assertEqual(0, code)
        self.assertIn('ls', stdout)
        self.assertEqual('', stderr)

    def test002_execute_wrong_local_command(self):
        with self.assertRaises(UnexpectedExit) as context:
            j.core.executors.run_local('random')

    def test003_execute_wrong_local_command_with_warn(self):
        code, stdout, stderr = j.core.executors.run_local('random', warn=True)
        self.assertEqual('', stdout)
        self.assertIn('random: command not found', stderr)

    @parameterized.expand([(True, ), (False, )])
    def test004_execute_local_command_with_hide(self, hide):
        capture = io.StringIO()
        sys.stdout = capture
        code, stdout, stderr = j.core.executors.run_local('which ls', hide=hide)
        output = capture.getvalue()
        capture.close()
        sys.stdout = sys.__stdout__
        if hide:
            self.assertEqual(output, '')
        else:
            self.assertEqual(output, stdout)

    @parameterized.expand([(True, ), (False, )])
    def test005_execute_local_command_with_echo(self, echo):
        capture = io.StringIO()
        sys.stdout = capture
        j.core.executors.run_local('which ls', echo=echo)
        output = capture.getvalue()
        capture.close()
        sys.stdout = sys.__stdout__
        if echo:
            self.assertIn('which ls', output)
        else:
            self.assertNotIn('which ls', output)

    def test006_execute_local_command_hide_overwrite_echo(self):
        capture = io.StringIO()
        sys.stdout = capture
        j.core.executors.run_local('which ls', echo=True, hide=True)
        output = capture.getvalue()
        capture.close()
        sys.stdout = sys.__stdout__
        self.assertEqual('', output)

    def test007_execute_local_command_with_env(self):
        code, stdout, stderr =j.core.executors.run_local('echo $PATH', env={'PATH': ''})
        self.assertEqual('\n', stdout)

        


