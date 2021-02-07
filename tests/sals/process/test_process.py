import string
import getpass
from math import ceil
from random import randint
from gevent import sleep

import pytest
from jumpscale.loader import j
from parameterized import parameterized
from tests.base_tests import BaseTests

SESSION_NAME = "testing"
TAIL_PROCESS_NAME = "tail"
PYTHON_SERVER_NAME = "http.server"
HOST = "127.0.0.1"


class ProcessTests(BaseTests):
    def setUp(self):
        self.user_to_clear = []
        j.core.executors.tmux.get_session(SESSION_NAME)

    def tearDown(self):
        j.core.executors.tmux.kill_session(SESSION_NAME)
        if self.get_process_pids(TAIL_PROCESS_NAME):
            j.sals.process.kill_all(TAIL_PROCESS_NAME)

        for user in self.user_to_clear:
            cmd = f"""sudo userdel  {user};
            sudo rm -rf /home/{user}"""
            j.sals.process.execute(cmd)

    def randstr(self):
        return j.data.idgenerator.nfromchoices(10, string.ascii_letters)

    def start_in_tmux(self, cmd):
        window_name = self.randstr()
        j.core.executors.tmux.execute_in_window(cmd, window_name, SESSION_NAME)
        sleep(1)

    def get_process_pids(self, process_name, full=False, user=None):
        self.info(f"user name: {process_name}")
        options = []
        if full:
            options.append("-f")
        if user:
            options.append(f"-u {user}")
        cmd = f"pgrep {' '.join(options)} '{process_name}'"
        rc, output, error = j.sals.process.execute(cmd)
        self.info(f"ourput: {output}, error: {error}, rc: {rc}")
        self.assertFalse(error)
        if not output:
            return []
        z_pids_str = " ".join(['"' + pid + '"' for pid in output.split()])  # excluding Dead processes
        cmd = f"ps -o s= -o pid= {z_pids_str} | sed -n 's/^[^ZT][[:space:]]\+//p'"
        rc, output, error = j.sals.process.execute(cmd)
        self.info(f"ourput: {output}, error: {error}, rc: {rc}")
        self.assertFalse(error)
        self.info(f"output: {output}")
        pids = list(map(int, output.split()))
        return pids

    def create_user(self, username, file_path):
        cmd = f"""sudo useradd {username};
        sudo mkdir -p /home/{username};
        sudo touch {file_path};
        """
        rc, _, error = j.sals.process.execute(cmd)
        self.assertFalse(rc, error)

    def get_ports_mapping(self):
        rc, output, error = j.sals.process.execute("netstat -tlnp | tail -n+3 | awk '{{ print $4 }}'")  # ip:port
        self.assertFalse(rc, error)
        ips_ports = output.splitlines()

        rc, output, error = j.sals.process.execute("netstat -tlnp | tail -n+3 | awk '{{ print $7 }}'")  # PID/process
        self.assertFalse(rc, error)
        pids_processes = output.splitlines()

        ports = {}
        for i, ip_port in enumerate(ips_ports):
            ports[i] = int(ip_port.split(":")[-1])

        pids = {}
        for i, pid_process in enumerate(pids_processes):
            pids[i] = pid_process.split("/")[0]

        mapping = {}
        for i in pids.keys():
            if pids[i] != "-":
                pid = int(pids[i])
                if pid not in mapping.keys():
                    mapping[pid] = []
                mapping[pid].append(ports[i])

        return mapping

    def test01_execute(self):
        """Test case for executing command.

        **Test Scenario**

        - Execute command.
        - Check the command result.
        """
        self.info("Execute command.")
        rc, stdout, stderr = j.sals.process.execute("which ls")

        self.info("Check the command result.")
        self.assertFalse(rc, stderr)
        self.assertIn("ls", stdout)

    def test02_execute_with_env(self):
        """Test case for executing command with environment variable.

        **Test Scenario**

        - Execute command with environment variable.
        - Check that the environment varible is exist.
        """
        self.info("Execute command with environment variable.")
        env_name = self.randstr()
        env_value = self.randstr()
        rc, stdout, stderr = j.sals.process.execute(f"echo ${env_name}", env={env_name: env_value})

        self.info("Check that the environment varible is exist.")
        self.assertFalse(rc, stderr)
        self.assertIn(env_value, stdout.strip())

    def test_03_execute_with_timeout(self):
        """Test case for executing command with timeout.

        **Test Scenario**

        - Execute command with timeout.
        - Make sure that the command will raise timeout error.
        """
        self.info("Execute command with timeout.")
        self.info("Make sure that the command will raise timeout error.")
        with self.assertRaises(Exception):
            j.sals.process.execute("sleep 3", timeout=1)

    def test_04_execute_with_die(self):
        """Test case for executing command with die.

        **Test Scenario**

        - Execute command with die.
        - Make sure that the command will raise error.
        """
        self.info("Execute command with die.")
        self.info("Make sure that the command will raise error.")
        dir_name = self.randstr()
        with self.assertRaises(Exception):
            j.sals.process.execute(f"ls {dir_name}", die=True)

    def test_05_execute_with_cwd(self):
        """Test case for executing command with working directory.

        **Test Scenario**

        - Create a directory with one file.
        - Execute command in the directory has been created.
        - Check that the command will run on the directory has been created.
        - Delete created file and directory.
        """
        self.info("Create a directory with one file.")
        dir_name = self.randstr()
        file_name = self.randstr()
        dir_path = j.sals.fs.join_paths("/tmp", dir_name)
        file_path = j.sals.fs.join_paths(dir_path, file_name)
        j.sals.fs.mkdir(dir_path)
        j.sals.fs.touch(file_path)

        self.info("Execute command in the directory has been created.")
        rc, stdout, stderr = j.sals.process.execute(f"ls {dir_path}")

        self.info("Check that the command will run on the directory has been created.")
        self.assertFalse(rc, stderr)
        self.assertIn(file_name, stdout.strip())

        self.info("Delete created file and directory")
        j.sals.fs.rmtree(dir_path)

    def test_06_check_for_pid_process(self):
        """Test case for checking that the pid and process name are belong to the same process.

        **Test Scenario**

        - Start a process in tmux.
        - Get process id.
        - Check that the pid and process name are belong to the same process.
        """
        self.info("Start a process in tmux.")
        cmd = f"{TAIL_PROCESS_NAME} -f /dev/null"
        self.start_in_tmux(cmd)

        self.info("Get process id.")
        pids = self.get_process_pids(TAIL_PROCESS_NAME)
        self.assertEqual(len(pids), 1)

        self.info("Check that the pid and process name are belong to the same process.")
        self.assertTrue(j.sals.process.check_process_for_pid(pid=pids[0], process_name=TAIL_PROCESS_NAME))

    def test_07_check_running(self):
        """Test case for checking that process is running.

        **Test Scenario**

        - Start a process in tmux.
        - Check that the process is running with one minimum instance, should be True.
        - Check that the process is running with two minimum instance, should be False.
        - Start another process in tmux.
        - Check that the process is running with two minimum instance, should be True.
        """
        self.info("Start a process in tmux.")
        cmd = f"{TAIL_PROCESS_NAME} -f /dev/null"
        self.start_in_tmux(cmd)

        self.info("Check that the process is running with one minimum instance, should be True.")
        self.assertTrue(j.sals.process.check_running(TAIL_PROCESS_NAME, min=1))

        self.info("Check that the process is running with two minimum instance, should be False.")
        self.assertFalse(j.sals.process.check_running(TAIL_PROCESS_NAME, min=2))

        self.info("Start another process in tmux.")
        self.start_in_tmux(cmd)

        self.info("Check that the process is running with two minimum instance, should be True.")
        self.assertTrue(j.sals.process.check_running(TAIL_PROCESS_NAME, min=2))

    def test_08_check_start_stop(self):
        """Test case for checking starting and stopping command.

        **Test Scenario**

        - Start a process in tmux with check_start.
        - Check that the process has been started.
        - Stop the process.
        - Check that the process has been stopped.
        - Start a process again in tmux with nrinstances=2, should fail.
        """
        self.info("Start a process in tmux with check_start.")
        window_name = self.randstr()
        start_cmd = f"tmux new-window -t {SESSION_NAME} -d -n {window_name} '{TAIL_PROCESS_NAME} -f /dev/null'"
        j.sals.process.check_start(cmd=start_cmd, filterstr=TAIL_PROCESS_NAME, n_instances=1)

        self.info("Check that the process has been started.")
        pids = self.get_process_pids(TAIL_PROCESS_NAME)
        self.assertEqual(len(pids), 1)

        self.info("Stop the process.")
        stop_cmd = f"tmux kill-window -t {window_name}"
        j.sals.process.check_stop(stop_cmd, filterstr=TAIL_PROCESS_NAME)

        self.info("Check that the process has been stopped.")
        pids = self.get_process_pids(TAIL_PROCESS_NAME)
        self.assertFalse(pids, "Process is not stopped")

        self.info("Start a process again in tmux with nrinstances=2, should fail.")
        with self.assertRaises(Exception):
            j.sals.process.check_start(cmd=start_cmd, filterstr=TAIL_PROCESS_NAME, n_instances=2)

    def test_09_get_process_environ(self):
        """Test case for getting process environment variables.

        **Test Scenario**

        - Start a tail command with environment variable.
        - Check that the process has been started and get its pid.
        - Get this process environ with its pid.
        - Check that the environment variable has been set is in process environ.
        """
        self.info("Start a tail command with environment variable.")
        cmd = f"{TAIL_PROCESS_NAME} -f /dev/null &> /dev/null &"
        env_name = self.randstr()
        env_val = self.randstr()
        rc, _, error = j.sals.process.execute(cmd=cmd, env={env_name: env_val})
        self.assertFalse(rc, error)
        sleep(1)

        self.info("Check that the process has been started and get its pid.")
        pids = self.get_process_pids(TAIL_PROCESS_NAME)
        self.assertEqual(len(pids), 1, "tail didn't start")

        self.info("Get this process environ with its pid.")
        env = j.sals.process.get_environ(pids[0])

        self.info("Check that the environment variable has been set is in process environ.")
        self.assertIn(env_name, env.keys())
        self.assertEqual(env[env_name], env_val)

    def test_10_get_filtered_pids(self):
        """Test case for getting filtered process pid.

        **Test Scenario**

        - Start a tmux session with two python server process.
        - Check that the process has been started and get its pid.
        - Get this process pid with its name.
        - Check that there is two pids.
        - Get this process pid with its name and filtered with server port.
        - Check that only one server is found.
        """
        self.info("Start a tmux session with two python server process.")
        port_1 = randint(20000, 21000)
        port_2 = randint(22000, 23000)
        cmd = f"python3 -m {PYTHON_SERVER_NAME} {port_1}"
        self.start_in_tmux(cmd)
        cmd = f"python3 -m {PYTHON_SERVER_NAME} {port_2}"
        self.start_in_tmux(cmd)
        self.assertTrue(j.sals.nettools.wait_connection_test(HOST, port_1, 2))
        self.assertTrue(j.sals.nettools.wait_connection_test(HOST, port_2, 2))

        self.info("Check that the process has been started and get its pid.")
        pids = self.get_process_pids(PYTHON_SERVER_NAME, full=True)
        self.assertEqual(len(pids), 2)

        self.info("Get this process pid with its name.")
        server_pids = j.sals.process.get_filtered_pids(PYTHON_SERVER_NAME)

        self.info("Check that there is two pids.")
        self.assertEqual(len(server_pids), 2)
        self.assertEqual(sorted(pids), sorted(server_pids))

        self.info("Get this process pid with its name and filtered with server port.")
        server_pid = j.sals.process.get_filtered_pids(PYTHON_SERVER_NAME, excludes=[str(port_1)])

        self.info("Check that only one server is found.")
        self.assertEqual(len(server_pid), 1)
        self.assertIn(server_pid[0], pids)

    def test_11_get_memory_usage(self):
        """Test case for getting memory usage.

        **Test Scenario**

        - Get memory usage from SALS process.
        - Get memory usage from 'free' command.
        - Check that memory usage from both ways almost the same.
        """
        self.info("Get memory usage from SALS process.")
        memory_usage = j.sals.process.get_memory_usage()

        self.info("Get memory usage from 'free' command.")
        cmd = "free"
        rc, output, error = j.sals.process.execute(cmd)
        self.assertFalse(rc, error)
        self.assertTrue(output)
        names = output.splitlines()[0].split()
        values = output.splitlines()[1].split()[1:]

        memory_info = {}
        for i, name in enumerate(names):
            memory_info[name] = int(values[i])

        total = ceil(memory_info["total"] / (1024 ** 2))
        used = ceil(memory_info["used"] / (1024 ** 2))
        available = ceil(memory_info["available"] / (1024 ** 2))
        percent = (total - available) / (total) * 100

        self.info("Check that memory usage from both ways almost the same.")
        self.assertEqual(memory_usage["total"], total)
        self.assertAlmostEqual(memory_usage["used"], used, delta=1)
        self.assertAlmostEqual(memory_usage["percent"], percent, delta=5)

    #  @pytest.mark.skip("https://github.com/threefoldtech/js-ng/issues/467")
    def test_12_get_processes_info(self):
        """Test case for getting processes info.

        **Test Scenario**

        - Start python server in tmux.
        - Check that the server has been started.
        - Get processes self.info using SALS process.
        - Check that the python server is in the processes self.info.
        - Get the current process using SALS process.
        - Check that this process in processes self.info.
        """
        self.info("Start python server in tmux.")
        port = randint(10000, 20000)
        cmd = f"python3 -m {PYTHON_SERVER_NAME} {port}"
        self.start_in_tmux(cmd)
        self.assertTrue(j.sals.nettools.wait_connection_test(HOST, port, 2))

        self.info("Check that the server has been started.")
        pids = self.get_process_pids(PYTHON_SERVER_NAME, full=True)
        self.assertEqual(len(pids), 1)

        self.info("Get processes info using SALS process.")
        processes_info = j.sals.process.get_processes_info(limit=-1)

        self.info("Check that the python server is in the processes info.")
        found = False
        for process_info in processes_info:
            if process_info["pid"] == pids[0]:
                found = True
                break
        self.assertTrue(found)
        self.assertEqual(process_info["name"], "python3")
        self.assertEqual(process_info["ports"], [{"port": port, "status": "LISTEN"}])

        self.info("Get the current process using SALS process.")
        my_process = j.sals.process.get_my_process()

        self.info("Check that this process in processes self.info.")
        found = False
        for process_info in processes_info:
            if process_info["pid"] == my_process.pid:
                found = True
                break
        self.assertTrue(found)
        self.assertEqual(process_info["name"], my_process.name())

    def test_13_get_kill_process_by_port(self):
        """Test case for getting and killing process by its port.

        **Test Scenario**

        - Start python server in tmux.
        - Check that the server has been started.
        - Get the process by port.
        - Get pid of the process by port.
        - Check that the python server pid is the same one from SALS process.
        - Kill the server by port.
        - Check that the server pid is not exist.
        """
        self.info("Start python server in tmux.")
        port = randint(10000, 20000)
        cmd = f"python3 -m {PYTHON_SERVER_NAME} {port}"
        self.start_in_tmux(cmd)
        self.assertTrue(j.sals.nettools.wait_connection_test(HOST, port, 2))

        self.info("Check that the server has been started.")
        pids = self.get_process_pids(PYTHON_SERVER_NAME, full=True)
        self.assertEqual(len(pids), 1)
        self.assertTrue(j.sals.process.is_port_listening(port))

        self.info("Get the process by port.")
        process = j.sals.process.get_process_by_port(port)

        self.info("Get pid of the process by port.")
        process_pid = j.sals.process.get_pid_by_port(port)

        self.info("Check that the python server pid is the same one from SALS process.")
        self.assertEqual(process_pid, pids[0])
        self.assertEqual(process.pid, pids[0])
        self.assertEqual(process.name(), "python3")

        self.info("Kill the server by port.")
        killed = j.sals.process.kill_process_by_port(port)

        self.info("Check that the server pid is not exist.")
        self.assertTrue(killed)
        pids = self.get_process_pids(PYTHON_SERVER_NAME, full=True)
        self.assertFalse(pids)
        self.assertFalse(j.sals.process.is_port_listening(port))

    def test_14_is_installed(self):
        """Test case for is_installed method.

        **Test Scenario**

        - Check that a package should be installed with js-ng.
        - Check that any random name is not installed.
        """
        self.info("Check that a package should be installed with js-ng.")
        self.assertTrue(j.sals.process.is_installed("tmux"))

        self.info("Check that any random name is not installed.")
        unkown_package = self.randstr()
        self.assertFalse(j.sals.process.is_installed(unkown_package))

    def test_15_get_kill_process_by_pids(self):
        """Test case for getting and killing process by pids.

        **Test Scenario**

        - Start a tail process in tmux.
        - Check that the process has been started.
        - Get the process pids.
        - Check that the process pid is alive.
        - Kill the process.
        - Check that the process has been killed.
        """
        self.info("Start a tail process in tmux.")
        cmd = f"{TAIL_PROCESS_NAME} -f /dev/null"
        self.start_in_tmux(cmd)

        self.info("Check that the process has been started.")
        pids = self.get_process_pids(TAIL_PROCESS_NAME)
        self.assertEqual(len(pids), 1)

        self.info("Get the process pids.")
        pids = j.sals.process.get_pids(TAIL_PROCESS_NAME)
        self.assertTrue(pids)

        self.info("Check that the process pid is alive.")
        self.assertTrue(j.sals.process.is_alive(pids[0]))

        self.info("Kill the process.")
        killed = j.sals.process.kill(pids[0])
        self.assertTrue(killed)
        sleep(1)

        self.info("Check that the process has been killed.")
        self.assertFalse(j.sals.process.is_alive(pids[0]))
        pids = j.sals.process.get_pids(TAIL_PROCESS_NAME)
        self.assertFalse(pids)

    @parameterized.expand(["kill_all", "kill_user_processes", "kill_process_by_name"])
    @pytest.mark.admin
    def test_16_get_kill_user_process(self, kill_method):
        """Test case for getting and killing user process/ killall processes.

        **Test Scenario**

        - Start a tail process in tmux with the current user.
        - Check that the process has been started.
        - Create a user.
        - Start another tail process in tmux with new user.
        - Check that the process has been started.
        - Get the user process.
        - Check that the process is the new user process.
        - Kill the user/killall process, and check that the target process killed.
        """
        self.info("Start a tail process in tmux with the current user.")
        cmd = f"{TAIL_PROCESS_NAME} -f /dev/null"
        self.start_in_tmux(cmd)

        self.info("Check that the process has been started.")
        pids = self.get_process_pids(TAIL_PROCESS_NAME)
        self.assertEqual(len(pids), 1)

        self.info("Create a user.")
        username = self.randstr()
        file_path = j.sals.fs.join_paths("/home", username, self.randstr())
        self.create_user(username, file_path)
        self.user_to_clear.append(username)

        self.info("Start another tail process in tmux with new user.")
        cmd = f"sudo -u {username} {TAIL_PROCESS_NAME} -f {file_path}"
        self.start_in_tmux(cmd)

        self.info("Check that the process has been started.")
        cmd = f"ps -u {username} | grep tail | awk '{{ print $1 }}'"
        rc, output, error = j.sals.process.execute(cmd)
        self.assertFalse(rc, error)
        self.assertTrue(output)
        user_pid = int(output.strip())

        self.info("Get the user process.")
        user_pids = [p.pid for p in j.sals.process.get_user_processes(username)]
        self.assertEqual(len(user_pids), 1)

        self.info("Check that the process is the new user process.")
        self.assertIn(user_pid, user_pids)

        self.info("Kill the user/killall process, and check that the target process killed.")

        if kill_method == "kill_user_processes":
            j.sals.process.kill_user_processes(username)
            sleep(1)
            self.assertFalse(j.sals.process.is_alive(user_pid))
            self.assertTrue(j.sals.process.is_alive(pids[0]))
        else:
            kill_method = getattr(j.sals.process, kill_method)
            kill_method(TAIL_PROCESS_NAME)
            sleep(1)
            self.assertFalse(j.sals.process.is_alive(user_pid))
            self.assertFalse(j.sals.process.is_alive(pids[0]))

    def test_17_check_in_docker(self):
        """Test case for Checking if in docker or in host.

        **Test Scenario**

        - Check if in docker/host with dockerenv file.
        - Check if in docker/host with Sals.
        - Check that the result from both ways are the same.
        """
        self.info("Check if in docker/host with dockerenv file.")
        in_docker = j.sals.fs.exists("/.dockerenv")

        self.info("Check if in docker/host with Sals.")
        indocker = j.sals.process.in_docker()
        inhost = j.sals.process.in_host()

        self.info("Check that the result from both ways are the same.")
        self.assertEqual(indocker, in_docker)
        self.assertNotEqual(inhost, in_docker)

    def test_18_ps_find(self):
        """Test case for Checking if process exists.

        **Test Scenario**

        - Start a tail process.
        - Check that the process has been started.
        - Check that the process exists, should be found.
        - Check for a random name, should not be found.
        """
        self.info("Start a tail process.")
        cmd = f"{TAIL_PROCESS_NAME} -f /dev/null"
        self.start_in_tmux(cmd)

        self.info("Check that the process has been started.")
        pids = self.get_process_pids(TAIL_PROCESS_NAME)
        self.assertEqual(len(pids), 1)

        self.info("Check that the process exists, should be found.")
        self.assertTrue(j.sals.process.ps_find(TAIL_PROCESS_NAME))

        self.info("Check for a random name, should not be found.")
        self.assertFalse(j.sals.process.ps_find(self.randstr()))

    def test_19_set_env_var(self):
        """Test case for setting environment variable.

        **Test Scenario**

        - Set environment variable with SAL.
        - Check that the environment variable is set.
        - Set environment variable with non equal length, should fail.
        """
        self.info("Set environment variable with SAL.")
        names = [self.randstr() for i in range(5)]
        values = [self.randstr() for i in range(5)]
        j.sals.process.set_env_var(names, values)

        self.info("Check that the environment variable is set.")
        for i, name in enumerate(names):
            _, output, _ = j.sals.process.execute(f"echo ${name}")
            self.assertEqual(output.strip(), values[i])

        self.info("Set environment variable with non equal length, should fail.")
        names = [self.randstr() for i in range(5)]
        values = [self.randstr() for i in range(4)]
        with self.assertRaises(Exception):
            j.sals.process.set_env_var(names, values)

    def test_20_get_ports_mapping(self):
        """Test case for getting port mapping.

        **Test Scenario**

        - Start python server.
        - Check that the server has been started.
        - Start redis server.
        - Check that the server has been started.
        - Get port mapping with netstat command.
        - Get port mapping with SAL.
        - Check that the result from both ways are the same.
        """
        self.info("Start python server.")
        python_port = randint(10000, 20000)
        cmd = f"python3 -m {PYTHON_SERVER_NAME} {python_port}"
        self.start_in_tmux(cmd)
        self.assertTrue(j.sals.nettools.wait_connection_test(HOST, python_port, 2))

        self.info("Check that the server has been started.")
        python_server_pids = self.get_process_pids(PYTHON_SERVER_NAME, full=True)
        self.assertEqual(len(python_server_pids), 1)

        self.info("Start redis server.")
        process_name = "redis-server"
        redis_port = randint(2001, 3000)
        cmd = f"{process_name} --port {redis_port}"
        self.start_in_tmux(cmd)
        self.assertTrue(j.sals.nettools.wait_connection_test(HOST, redis_port, 2))

        self.info("Check that the server has been started.")
        j.sals.process.is_port_listening(redis_port)

        self.info("Get port mapping with netstat command.")
        netstat_mapping = self.get_ports_mapping()

        self.info("Get port mapping with SAL.")
        process_ports_mapping = j.sals.process.get_ports_mapping()
        sal_mapping = {}
        for process in process_ports_mapping.keys():
            sal_mapping[process.pid] = process_ports_mapping[process]

        self.info("Stop redis server.")
        j.sals.process.kill_process_by_port(redis_port)

        self.info("Check that the result from both ways are the same.")
        for key in sal_mapping.keys():
            self.assertEqual(sorted(sal_mapping[key]), sorted(netstat_mapping[key]))

    def test_21_get_defunct_processes(self):
        """Test case for getting defunct processes.

        **Test Scenario**

        - Start a dummy zombie process.
        - Get zombie processes with ps command.
        - Get zombie processes with sal.
        - Check that the both ways have the same result.
        """
        self.info("Start a dummy zombie process.")
        cmd = "sleep 1 & exec /bin/sleep 3"
        self.start_in_tmux(cmd)

        self.info("Get zombie processes with ps command.")
        cmd = "ps aux | grep -w Z | grep -v grep | awk '{{ print $2 }}'"
        rc, output, error = j.sals.process.execute(cmd)
        self.assertFalse(rc, error)
        pids = list(map(int, output.splitlines()))

        self.info("Get zombie processes with sal.")
        sal_pids = j.sals.process.get_defunct_processes()

        self.info("Check that the both ways have the same result.")
        self.assertEqual(sorted(sal_pids), pids)

    @parameterized.expand(["sorted", "regex"])
    @pytest.mark.admin
    def test_22_get_sorted_pids(self, type_):
        """Test case for getting sorted pids by username.

        **Test Scenario**

        - Start a tail process from the currnet user.
        - Create two users and start tail process for each user.
        - Get each user pids.
        - Get pids sorted with username.
        - Check that the pids are sorted.
        - Get tail pids with regex filter.
        - Check that only pids that match the regex are returned.
        """
        self.info("Start a tail process from the currnet user.")
        user_pids = {}
        current_user = getpass.getuser()
        cmd = f"{TAIL_PROCESS_NAME} -f /dev/null"
        self.start_in_tmux(cmd)

        self.info("Create two users and start tail process for each user.")
        user_1 = self.randstr()
        file_path_1 = j.sals.fs.join_paths("/home", user_1, self.randstr())
        self.create_user(user_1, file_path_1)
        self.user_to_clear.append(user_1)
        cmd = f"sudo -u {user_1} {TAIL_PROCESS_NAME} -f {file_path_1}"
        self.start_in_tmux(cmd)

        user_2 = self.randstr()
        file_path_2 = j.sals.fs.join_paths("/home", user_2, self.randstr())
        self.create_user(user_2, file_path_2)
        self.user_to_clear.append(user_2)
        cmd = f"sudo -u {user_2} {TAIL_PROCESS_NAME} -f {file_path_2}"
        self.start_in_tmux(cmd)

        self.info("Get each user pids.")
        user_pids[user_1] = self.get_process_pids(TAIL_PROCESS_NAME, user=user_1)

        user_pids[user_2] = self.get_process_pids(TAIL_PROCESS_NAME, user=user_2)

        user_pids[current_user] = self.get_process_pids(TAIL_PROCESS_NAME, user=current_user)

        if type_ == "sorted":
            self.info("Get pids sorted with username.")
            pids = j.sals.process.get_pids_filtered_sorted(TAIL_PROCESS_NAME, sortkey="euser")
        else:
            self.info("Get tail pids with regex filter.")
            pids = j.sals.process.get_pids_filtered_by_regex([f"{TAIL_PROCESS_NAME}*"])

        users = sorted([current_user, user_1, user_2])
        sorted_pids = []
        for user in users:
            # if user == current_user and type_ == "sorted":
            #     sorted_pids.extend(user_pids[user])
            # if user == current_user and type_ == "regex":
            #     sorted_pids.append(user_pids[user][0])
            # else:
            sorted_pids.extend(user_pids[user])
        if type_ == "sorted":
            self.info("Check that the pids are sorted.")
            self.assertEqual(pids, sorted_pids)
        else:
            self.info("Check that only pids that match the regex are returned.")
            self.assertEqual(pids, sorted(sorted_pids))
