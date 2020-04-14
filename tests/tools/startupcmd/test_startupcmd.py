import unittest

from jumpscale.god import j


class TestStartupCmd(unittest.TestCase):
    def setUp(self):
        self.instances = []
        self.run_cmd = "python3 -m http.server 0"

    def _get_instance(self):
        instance_name = j.data.random_names.random_name()
        self.instances.append(instance_name)

        cmd = j.tools.startupcmd.new(instance_name)
        return cmd

    def _get_port(self, proc):
        conn = proc.connections()[0]
        return conn.laddr[1]

    def test001_startup_cmd(self):
        cmd = self._get_instance()

        cmd.start_cmd = self.run_cmd

        cmd.start()

        self.assertTrue(cmd.is_running())
        self.assertTrue(cmd.pid)
        self.assertTrue(cmd.process)

        proc_port = self._get_port(cmd.process)
        cmd.check_cmd = f"curl -I http://0.0.0.0:{proc_port}"
        self.assertTrue(cmd.is_running())

        cmd.stop()

        self.assertFalse(cmd.pid)
        self.assertFalse(cmd.process)

        self.assertFalse(cmd.is_running())

    def test002_attach_cmd(self):
        attached_cmd = self._get_instance()

        attached_cmd.start_cmd = self.run_cmd

        attached_cmd.start()

        cmd = self._get_instance()

        cmd.ports = [self._get_port(attached_cmd.process)]

        self.assertTrue(cmd.is_running())

        self.assertTrue(cmd.process)

        cmd.stop()

        self.assertFalse(cmd.is_running())

    def tearDown(self):
        for instance in self.instances:
            j.tools.startupcmd.delete(instance)
