import os
import string
from math import ceil
from random import randint
from subprocess import PIPE, run
from time import sleep
from unittest import TestCase

from jumpscale.loader import j
from parameterized import parameterized

SESSION_NAME = "testing_process"


def info(msg):
    j.logger.info(msg)


def randstr():
    return j.data.idgenerator.nfromchoices(10, string.ascii_letters)


def execute(cmd):
    response = run(cmd, stdout=PIPE, stderr=PIPE, shell=True, universal_newlines=True)
    output = response.stdout
    error = response.stderr
    rc = response.returncode
    return rc, output, error


class ProcessTests(TestCase):
    def setUp(self):
        self.user_to_clear = []
        cmd = f"tmux new-session -d -s {SESSION_NAME}"
        execute(cmd)

    def tearDown(self):
        cmd = f"tmux kill-session -t {SESSION_NAME}"
        execute(cmd)
        cmd = f"ps -aux | grep -v grep | grep tail | awk '{{ print $2 }}'"
        _, output, _ = execute(cmd)
        tail_processes = output.splitlines()
        if tail_processes:
            execute("pkill tail")

        for user in self.user_to_clear:
            cmd = f"""sudo userdel  {user};
            sudo rm -rf /home/{user}"""
            execute(cmd)

    def start_in_tmux(self, cmd):
        window_name = randstr()
        cmd = f"tmux new-window -d -t {SESSION_NAME} -n {window_name} '{cmd}'"
        rc, _, error = execute(cmd)
        self.assertFalse(rc, error)
        sleep(1)

    def get_process_pids(self, process_name):
        info("Get process id.")
        cmd = f"ps -aux | grep {process_name} | grep -v grep | awk '{{ print $2 }}'"
        rc, output, error = execute(cmd)
        self.assertFalse(rc, error)
        pids = list(map(int, output.splitlines()))
        return pids

    def create_user(self, username, file_path):
        cmd = f"""sudo useradd {username};
        sudo mkdir -p /home/{username};
        sudo touch {file_path};
        """
        rc, _, error = execute(cmd)
        self.assertFalse(rc, error)

    def get_ports_mapping(self):
        rc, output, error = execute("netstat -tlnp | tail -n+3 | awk '{{ print $4 }}'")  # ip:port
        self.assertFalse(rc, error)
        ips_ports = output.splitlines()

        rc, output, error = execute("netstat -tlnp | tail -n+3 | awk '{{ print $7 }}'")  # PID/process
        self.assertFalse(rc, error)
        pids_processes = output.splitlines()

        ports = []
        for ip_port in ips_ports:
            ports.append(int(ip_port.split(":")[-1]))

        pids = []
        for pid_process in pids_processes:
            pids.append(int(pid_process.split("/")[0]))

        mapping = {}
        for i, pid in enumerate(pids):
            if pid not in mapping.keys():
                mapping[pid] = []
            mapping[pid].append(ports[i])

        return mapping

    def test01_execute(self):
        """Test case for executing command.

        **Test Scenario**
        #. Execute command.
        #. Check the command result.
        """
        info("Execute command.")
        rc, stdout, stderr = j.sals.process.execute("which ls")

        info("Check the command result.")
        self.assertFalse(rc, stderr)
        self.assertIn("ls", stdout)

    def test02_execute_with_env(self):
        """Test case for executing command with environment variable.

        **Test Scenario**
        #. Execute command with environment variable.
        #. Check that the environment varible is exist.
        """
        info("Execute command with environment variable.")
        env_name = randstr()
        env_value = randstr()
        rc, stdout, stderr = j.sals.process.execute(f"echo ${env_name}", env={env_name: env_value})

        info("Check that the environment varible is exist.")
        self.assertFalse(rc, stderr)
        self.assertIn(env_value, stdout.strip())

    def test_03_execute_with_timeout(self):
        """Test case for executing command with timeout.

        **Test Scenario**
        #. Execute command with timeout.
        #. Make sure that the command will raise timeout error.
        """
        info("Execute command with timeout.")
        info("Make sure that the command will raise timeout error.")
        with self.assertRaises(Exception):
            j.sals.process.execute("sleep 3", timeout=1)

    def test_04_execute_with_die(self):
        """Test case for executing command with die.

        **Test Scenario**
        #. Execute command with die.
        #. Make sure that the command will raise error.
        """
        info("Execute command with die.")
        info("Make sure that the command will raise error.")
        dir_name = randstr()
        with self.assertRaises(Exception):
            j.sals.process.execute(f"ls {dir_name}", die=True)

    def test_05_execute_with_cwd(self):
        """Test case for executing command with working directory.

        **Test Scenario**
        #. Create a directory with one file.
        #. Execute command in the directory has been created.
        #. Check that the command will run on the directory has been created.
        #. Delete created file and directory.
        """
        info("Create a directory with one file.")
        dir_name = randstr()
        file_name = randstr()
        dir_path = os.path.join("/tmp", dir_name)
        file_path = os.path.join(dir_path, file_name)
        os.mkdir(dir_path)
        open(file_path, "w").close()

        info("Execute command in the directory has been created.")
        rc, stdout, stderr = j.sals.process.execute(f"ls {dir_path}")

        info("Check that the command will run on the directory has been created.")
        self.assertFalse(rc, stderr)
        self.assertIn(file_name, stdout.strip())

        info("Delete created file and directory")
        os.remove(file_path)
        os.rmdir(dir_path)

    def test_06_check_for_pid_process(self):
        """Test case for checking that the pid and process name are belong to the same process.

        **Test Scenario**
        #. Start a process in tmux.
        #. Get process id.
        #. Check that the pid and process name are belong to the same process.
        """
        info("Start a process in tmux.")
        process_name = "tail"
        cmd = f"{process_name} -f /dev/null"
        self.start_in_tmux(cmd)

        info("Get process id.")
        pids = self.get_process_pids(process_name)
        self.assertEqual(len(pids), 1)

        info("Check that the pid and process name are belong to the same process.")
        self.assertTrue(j.sals.process.check_process_for_pid(pid=pids[0], process_name=process_name))

    def test_07_check_running(self):
        """Test case for checking that process is running.

        *Test Scenario**
        #. Start a process in tmux.
        #. Check that the process is running with one minimum instance, should be True.
        #. Check that the process is running with two minimum instance, should be False.
        #. Start another process in tmux.
        #. Check that the process is running with two minimum instance, should be True.
        """
        info("Start a process in tmux.")
        process_name = "tail"
        cmd = f"{process_name} -f /dev/null"
        self.start_in_tmux(cmd)

        info("Check that the process is running with one minimum instance, should be True.")
        self.assertTrue(j.sals.process.check_running(process_name, min=1))

        info("Check that the process is running with two minimum instance, should be False.")
        self.assertFalse(j.sals.process.check_running(process_name, min=2))

        info("Start another process in tmux.")
        self.start_in_tmux(cmd)

        info("Check that the process is running with two minimum instance, should be True.")
        self.assertTrue(j.sals.process.check_running(process_name, min=2))

    def test_08_check_start_stop(self):
        """Test case for checking starting and stopping command.

        *Test Scenario**
        #. Start a process in tmux with check_start.
        #. Check that the process has been started.
        #. Stop the process.
        #. Check that the process has been stopped.
        #. Start a process again in tmux with nrinstances=2, should fail.
        """
        info("Start a process in tmux with check_start.")
        window_name = randstr()
        process_name = "tail"
        start_cmd = f"tmux new-window -d -t {SESSION_NAME} -n {window_name} '{process_name} -f /dev/null'"
        j.sals.process.check_start(cmd=start_cmd, filterstr=process_name, nrinstances=1)

        info("Check that the process has been started.")
        pids = self.get_process_pids(process_name)
        self.assertEqual(len(pids), 1)

        info("Stop the process.")
        stop_cmd = f"tmux kill-window -t {window_name}"
        j.sals.process.check_stop(stop_cmd, filterstr=process_name)

        info("Check that the process has been stopped.")
        pids = self.get_process_pids(process_name)
        self.assertFalse(pids, "Process is not stopped")

        info("Start a process again in tmux with nrinstances=2, should fail.")
        with self.assertRaises(Exception):
            j.sals.process.check_start(cmd=start_cmd, filterstr=process_name, nrinstances=2)

    def test_09_get_process_environ(self):
        """Test case for getting process environment variables.

        *Test Scenario**
        #. Start a tail command with environment variable.
        #. Check that the process has been started and get its pid.
        #. Get this process environ with its pid.
        #. Check that the environment variable has been set is in process environ.
        """
        info("Start a tail command with environment variable.")
        process_name = "tail"
        cmd = f"{process_name} -f /dev/null &> /dev/null &"
        env_name = randstr()
        env_val = randstr()
        rc, _, error = j.sals.process.execute(cmd=cmd, env={env_name: env_val})
        self.assertFalse(rc, error)
        sleep(1)

        info("Check that the process has been started and get its pid.")
        pids = self.get_process_pids(process_name)
        self.assertEqual(len(pids), 1, "tail didn't start")

        info("Get this process environ with its pid.")
        env = j.sals.process.get_environ(pids[0])

        info("Check that the environment variable has been set is in process environ.")
        self.assertIn(env_name, env.keys())
        self.assertEqual(env[env_name], env_val)

    def test_10_get_filtered_pids(self):
        """Test case for getting filtered process pid.

        *Test Scenario**
        #. Start a tmux session with two python server process.
        #. Check that the process has been started and get its pid.
        #. Get this process pid with its name.
        #. Check that there is two pids.
        #. Get this process pid with its name and filtered with server port.
        #. Check that only one server is found.
        """
        info("Start a tmux session with two python server process.")
        process_name = "http.server"
        port_1 = randint(1000, 2000)
        port_2 = randint(2001, 3000)
        cmd = f"python3 -m {process_name} {port_1}"
        self.start_in_tmux(cmd)
        cmd = f"python3 -m {process_name} {port_2}"
        self.start_in_tmux(cmd)

        info("Check that the process has been started and get its pid.")
        pids = self.get_process_pids(process_name)
        self.assertEqual(len(pids), 2)

        info("Get this process pid with its name.")
        server_pids = j.sals.process.get_filtered_pids(process_name)

        info("Check that there is two pids.")
        self.assertEqual(len(server_pids), 2)
        self.assertEqual(sorted(pids), sorted(server_pids))

        info("Get this process pid with its name and filtered with server port.")
        server_pid = j.sals.process.get_filtered_pids(process_name, excludes=[str(port_1)])

        info("Check that only one server is found.")
        self.assertEqual(len(server_pid), 1)
        self.assertIn(server_pid[0], pids)

    def test_11_get_memory_usage(self):
        """Test case for getting memory usage.

        *Test Scenario**
        #. Get memory usage from SALS process.
        #. Get memory usage from 'free' command.
        #. Check that memory usage from both ways almost the same.
        """
        info("Get memory usage from SALS process.")
        memory_usage = j.sals.process.get_memory_usage()

        info("Get memory usage from 'free' command.")
        cmd = "free"
        rc, output, error = execute(cmd)
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

        info("Check that memory usage from both ways almost the same.")
        self.assertEqual(memory_usage["total"], total)
        self.assertAlmostEqual(memory_usage["used"], used, delta=1)
        self.assertAlmostEqual(memory_usage["percent"], percent, delta=5)

    def test_12_get_processes_info(self):
        """Test case for getting processes info.

        *Test Scenario**
        #. Start python server in tmux.
        #. Check that the server has been started.
        #. Get processes info using SALS process.
        #. Check that the python server is in the processes info.
        #. Get the current process using SALS process.
        #. Check that this process in processes info.
        """
        info("Start python server in tmux.")
        process_name = "http.server"
        port = randint(1000, 2000)
        cmd = f"python3 -m {process_name} {port}"
        self.start_in_tmux(cmd)

        info("Check that the server has been started.")
        pids = self.get_process_pids(process_name)
        self.assertEqual(len(pids), 1)

        info("Get processes info using SALS process.")
        processes_info = j.sals.process.get_processes_info()

        info("Check that the python server is in the processes info.")
        found = False
        for process_info in processes_info:
            if process_info["pid"] == pids[0]:
                found = True
                break
        self.assertTrue(found)
        self.assertEqual(process_info["name"], "python3")
        self.assertEqual(process_info["ports"], [{"port": port, "status": "LISTEN"}])

        info("Get the current process using SALS process.")
        my_process = j.sals.process.get_my_process()

        info("Check that this process in processes info.")
        found = False
        for process_info in processes_info:
            if process_info["pid"] == my_process.pid:
                found = True
                break
        self.assertTrue(found)
        self.assertEqual(process_info["name"], my_process.name())

    def test_13_get_kill_process_by_port(self):
        """Test case for getting and killing process by its port.

        *Test Scenario**
        #. Start python server in tmux.
        #. Check that the server has been started.
        #. Get the process by port.
        #. Get pid of the process by port.
        #. Check that the python server pid is the same one from SALS process.
        #. Kill the server by port.
        #. Check that the server pid is not exist.
        """
        info("Start python server in tmux.")
        process_name = "http.server"
        port = randint(1000, 2000)
        cmd = f"python3 -m {process_name} {port}"
        self.start_in_tmux(cmd)

        info("Check that the server has been started.")
        pids = self.get_process_pids(process_name)
        self.assertEqual(len(pids), 1)
        self.assertTrue(j.sals.process.is_port_listening(port))

        info("Get the process by port.")
        process = j.sals.process.get_process_by_port(port)

        info("Get pid of the process by port.")
        process_pid = j.sals.process.get_pid_by_port(port)

        info("Check that the python server pid is the same one from SALS process.")
        self.assertEqual(process_pid, pids[0])
        self.assertEqual(process.pid, pids[0])
        self.assertEqual(process.name(), "python3")

        info("Kill the server by port.")
        killed = j.sals.process.kill_process_by_port(port)

        info("Check that the server pid is not exist.")
        self.assertTrue(killed)
        pids = self.get_process_pids(process_name)
        self.assertFalse(pids)
        self.assertFalse(j.sals.process.is_port_listening(port))

    def test_14_is_installed(self):
        """Test case for is_installed method.

        *Test Scenario**
        #. Check that a package should be installed with js-ng.
        #. Check that any random name is not installed.
        """
        info("Check that a package should be installed with js-ng.")
        self.assertTrue(j.sals.process.is_installed("tmux"))

        info("Check that any random name is not installed.")
        unkown_package = randstr()
        self.assertFalse(j.sals.process.is_installed(unkown_package))

    def test_15_get_kill_process_by_pids(self):
        """Test case for getting and killing process by pids.

        *Test Scenario**
        #. Start a tail process in tmux.
        #. Check that the process has been started.
        #. Get the process pids.
        #. Check that the process pid is alive.
        #. Kill the process.
        #. Check that the process has been killed
        """
        info("Start a tail process in tmux.")
        process_name = "tail"
        cmd = f"{process_name} -f /dev/null"
        self.start_in_tmux(cmd)

        info("Check that the process has been started.")
        pids = self.get_process_pids(process_name)
        self.assertEqual(len(pids), 1)

        info("Get the process pids.")
        pids = j.sals.process.get_pids(process_name)
        self.assertTrue(pids)

        info("Check that the process pid is alive.")
        self.assertTrue(j.sals.process.is_alive(pids[0]))

        info("Kill the process.")
        killed = j.sals.process.kill(pids[0])
        self.assertTrue(killed)
        sleep(1)

        info("Check that the process has been killed.")
        self.assertFalse(j.sals.process.is_alive(pids[0]))
        pids = j.sals.process.get_pids(process_name)
        self.assertFalse(pids)

    @parameterized.expand(["kill_all", "kill_user_processes", "kill_process_by_name"])
    def test_16_get_kill_user_process(self, kill_method):
        """Test case for getting and killing user process/ killall processes.

        *Test Scenario**
        #. Start a tail process in tmux with the current user.
        #. Check that the process has been started.
        #. Create a user.
        #. Start another tail process in tmux with new user.
        #. Check that the process has been started.
        #. Get the user process.
        #. Check that the process is the new user process.
        #. Kill the user/killall process, and check that the target process killed.
        """
        info("Start a tail process in tmux with the current user.")
        process_name = "tail"
        cmd = f"{process_name} -f /dev/null"
        self.start_in_tmux(cmd)

        info("Check that the process has been started.")
        pids = self.get_process_pids(process_name)
        self.assertEqual(len(pids), 1)

        info("Create a user.")
        username = randstr()
        file_path = os.path.join("/home", username, randstr())
        self.create_user(username, file_path)
        self.user_to_clear.append(username)

        info("Start another tail process in tmux with new user.")
        cmd = f"sudo -u {username} {process_name} -f {file_path}"
        self.start_in_tmux(cmd)

        info("Check that the process has been started.")
        cmd = f"ps -u {username} | grep tail | awk '{{ print $1 }}'"
        rc, output, error = execute(cmd)
        self.assertFalse(rc, error)
        self.assertTrue(output)
        user_pid = int(output.strip())

        info("Get the user process.")
        user_pids = j.sals.process.get_user_processes(username)
        self.assertEqual(len(user_pids), 1)

        info("Check that the process is the new user process.")
        self.assertIn(user_pid, user_pids)

        info("Kill the user/killall process, and check that the target process killed.")

        if kill_method == "kill_user_processes":
            j.sals.process.kill_user_processes(username)
            sleep(1)
            self.assertFalse(j.sals.process.is_alive(user_pid))
            self.assertTrue(j.sals.process.is_alive(pids[0]))
        else:
            kill_method = getattr(j.sals.process, kill_method)
            kill_method(process_name)
            sleep(1)
            self.assertFalse(j.sals.process.is_alive(user_pid))
            self.assertFalse(j.sals.process.is_alive(pids[0]))

    def test_17_check_in_docker(self):
        """Test case for Checking if in docker or in host.

        *Test Scenario**
        #. Check if in docker/host with dockerenv file.
        #. Check if in docker/host with Sals.
        #. Check that the result from both ways are the same.
        """
        info("Check if in docker/host with dockerenv file.")
        in_docker = os.path.exists("/.dockerenv")

        info("Check if in docker/host with Sals.")
        indocker = j.sals.process.in_docker()
        inhost = j.sals.process.in_host()

        info("Check that the result from both ways are the same.")
        self.assertEqual(indocker, in_docker)
        self.assertNotEqual(inhost, in_docker)

    def test_18_ps_find(self):
        """Test case for Checking if process exists.

        *Test Scenario**
        #. Start a tail process.
        #. Check that the process has been started.
        #. Check that the process exists, should be found.
        #. Check for a random name, should not be found.
        """
        info("Start a tail process.")
        process_name = "tail"
        cmd = f"{process_name} -f /dev/null"
        self.start_in_tmux(cmd)

        info("Check that the process has been started.")
        pids = self.get_process_pids(process_name)
        self.assertEqual(len(pids), 1)

        info("Check that the process exists, should be found.")
        self.assertTrue(j.sals.process.ps_find(process_name))

        info("Check for a random name, should not be found.")
        self.assertFalse(j.sals.process.ps_find(randstr()))

    def test_19_set_env_var(self):
        """Test case for setting environment variable.

        *Test Scenario**
        #. Set environment variable with SAL.
        #. Check that the environment variable is set.
        #. Set environment variable with non equal length, should fail.
        """
        info("Set environment variable with SAL.")
        names = [randstr() for i in range(5)]
        values = [randstr() for i in range(5)]
        j.sals.process.set_env_var(names, values)

        info("Check that the environment variable is set.")
        for i, name in enumerate(names):
            _, output, _ = execute(f"echo ${name}")
            self.assertEqual(output.strip(), values[i])

        info("Set environment variable with non equal length, should fail.")
        names = [randstr() for i in range(5)]
        values = [randstr() for i in range(4)]
        with self.assertRaises(Exception):
            j.sals.process.set_env_var(names, values)

    def test_20_get_ports_mapping(self):
        """Test case for getting port mapping.

        *Test Scenario**
        #. Start python server.
        #. Check that the server has been started.
        #. Start redis server.
        #. Check that the server has been started.
        #. Get port mapping with netstat command.
        #. Get port mapping with SAL.
        #. Check that the result from both ways are the same.
        """
        info("Start python server.")
        process_name = "http.server"
        python_port = randint(1000, 2000)
        cmd = f"python3 -m {process_name} {python_port}"
        self.start_in_tmux(cmd)

        info("Check that the server has been started.")
        python_server_pids = self.get_process_pids(process_name)
        self.assertEqual(len(python_server_pids), 1)

        info("Start redis server.")
        process_name = "redis-server"
        redis_port = randint(2001, 3000)
        cmd = f"{process_name} --port {redis_port}"
        self.start_in_tmux(cmd)

        info("Check that the server has been started.")
        j.sals.process.is_port_listening(redis_port)

        info("Get port mapping with netstat command.")
        netstat_mapping = self.get_ports_mapping()

        info("Get port mapping with SAL.")
        process_ports_mapping = j.sals.process.get_ports_mapping()
        sal_mapping = {}
        for process in process_ports_mapping.keys():
            sal_mapping[process.pid] = process_ports_mapping[process]

        info("Stop redis server.")
        j.sals.process.kill_process_by_port(redis_port)

        info("Check that the result from both ways are the same.")
        self.assertEqual(sal_mapping, netstat_mapping)

    def test_21_get_defunct_processes(self):
        """Test case for getting defunct processes.

        *Test Scenario**
        #. Start a dummy zombie process.
        #. Get zombie processes with ps command.
        #. Get zombie processes with sal.
        #. Check that the both ways have the same result.
        """
        info("Start a dummy zombie process.")
        cmd = "sleep 1 & exec /bin/sleep 3"
        self.start_in_tmux(cmd)

        info("Get zombie processes with ps command.")
        cmd = "ps aux | grep -w Z | grep -v grep | awk '{{ print $2 }}'"
        rc, output, error = execute(cmd)
        self.assertFalse(rc, error)
        pids = list(map(int, output.splitlines()))

        info("Get zombie processes with sal.")
        sal_pids = j.sals.process.get_defunct_processes()

        info("Check that the both ways have the same result.")
        self.assertEqual(sorted(sal_pids), pids)

    @parameterized.expand(["sorted", "regex"])
    def test_22_get_sorted_pids(self, type_):
        """Test case for getting sorted pids by username.

        *Test Scenario**
        #. Start a tail process from the currnet user.
        #. Create two users and start tail process for each user.
        #. Get each user pids.
        #. Get pids sorted with username.
        #. Check that the pids are sorted.
        #. Get tail pids with regex filter.
        #. Check that only pids that match the regex are returned.
        """
        info("Start a tail process from the currnet user.")
        user_pids = {}
        current_user = os.path.expanduser("~").strip("/").strip("/home/")
        process_name = "tail"
        cmd = f"{process_name} -f /dev/null"
        self.start_in_tmux(cmd)

        info("Create two users and start tail process for each user.")
        user_1 = randstr()
        file_path_1 = os.path.join("/home", user_1, randstr())
        self.create_user(user_1, file_path_1)
        self.user_to_clear.append(user_1)
        cmd = f"sudo -u {user_1} {process_name} -f {file_path_1}"
        self.start_in_tmux(cmd)

        user_2 = randstr()
        file_path_2 = os.path.join("/home", user_2, randstr())
        self.create_user(user_2, file_path_2)
        self.user_to_clear.append(user_2)
        cmd = f"sudo -u {user_2} {process_name} -f {file_path_2}"
        self.start_in_tmux(cmd)

        info("Get each user pids.")
        cmd = f"ps -u {user_1} | grep {process_name} | awk '{{ print $1 }}'"
        rc, output, error = execute(cmd)
        self.assertFalse(rc, error)
        self.assertTrue(output)
        user_pids[user_1] = int(output.strip())

        cmd = f"ps -u {user_2} | grep {process_name} | awk '{{ print $1 }}'"
        rc, output, error = execute(cmd)
        self.assertFalse(rc, error)
        self.assertTrue(output)
        user_pids[user_2] = int(output.strip())

        pids = self.get_process_pids(process_name)
        pids.remove(user_pids[user_1])
        pids.remove(user_pids[user_2])
        user_pids[current_user] = pids

        if type_ == "sorted":
            info("Get pids sorted with username.")
            pids = j.sals.process.get_pids_filtered_sorted(process_name, sortkey="euser")
        else:
            info("Get tail pids with regex filter.")
            pids = j.sals.process.get_pids_filtered_by_regex([f"{process_name}*"])

        users = sorted([current_user, user_1, user_2])
        sorted_pids = []
        for user in users:
            if user == current_user and type_ == "sorted":
                sorted_pids.extend(user_pids[user])
            elif user == current_user and type_ == "regex":
                sorted_pids.append(user_pids[user][0])
            else:
                sorted_pids.append(user_pids[user])
        if type_ == "sorted":
            info("Check that the pids are sorted.")
            self.assertEqual(pids, sorted_pids)
        else:
            info("Check that only pids that match the regex are returned.")
            self.assertEqual(pids, sorted(sorted_pids))
