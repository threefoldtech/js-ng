import unittest
import subprocess

from jumpscale.god import j


class TestStartupCmd(unittest.TestCase):
    def setUp(self):
        self.instances = []
        self.run_cmd = "python3 -m http.server"
        self.proc = None

    def _get_instance(self):
        instance_name = j.data.random_names.random_name()
        self.instances.append(instance_name)

        cmd = j.tools.startupcmd.new(instance_name)
        cmd._instance_name = instance_name  # Remove me when instance name is added to baseclasses
        return cmd

    def test001_startup_cmd(self):
        cmd = self._get_instance()

        cmd.start_cmd = self.run_cmd

        cmd.start()

        self.assertTrue(cmd.is_running())
        self.assertTrue(cmd.pid)
        self.assertTrue(cmd.process)

        cmd.check_cmd = "curl -I http://0.0.0.0:8000"
        self.assertTrue(cmd.is_running())

        cmd.stop()

        self.assertFalse(cmd.pid)
        self.assertFalse(cmd.process)

        self.assertFalse(cmd.is_running())

    def test002_attach_cmd(self):
        cmd = self._get_instance()

        cmd.ports = [8000]

        self.proc = subprocess.Popen(self.run_cmd.split(), stdout=subprocess.PIPE)

        self.assertTrue(cmd.is_running())

        self.assertTrue(cmd.process)

        cmd.stop()

        self.assertFalse(cmd.is_running())

    def tearDown(self):
        if self.proc:
            self.proc.kill()
        for instance in self.instances:
            j.tools.startupcmd.delete(instance)
