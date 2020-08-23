"""This module manages long running commands

To start a python http server
```
cmd = j.tools.startupcmd.get("cmd_name")

cmd.start_cmd = "python3 -m http.server"

cmd.start()

```

Check if it is running

```
cmd.is_running()
```

Two types of executor:
- tmux(default)
- foreground

You can attach to a running process by specufying correct `name`, `ports`, `process_strings`, `process_strings_regex`.
If it matches any of the above you would be able to perform available on that process.


- Special cases

you can add cmd.ports, cmd.process_strings_regex or cmd.process_strings_regex to reach the process pid
"""
from enum import Enum
from jumpscale.loader import j
from jumpscale.core.base import Base, fields

import time
from psutil import NoSuchProcess


class Executor(Enum):
    TMUX = "tmux"
    FOREGROUND = "foreground"


class StartupCmd(Base):
    start_cmd = fields.String()
    ports = fields.List(fields.Integer())
    executor = fields.Enum(Executor)
    check_cmd = fields.String()
    path = fields.String(default=j.core.dirs.TMPDIR)
    stop_cmd = fields.String()
    env = fields.Typed(dict, default={})
    timeout = fields.Integer(default=60)
    process_strings = fields.List(fields.String())
    process_strings_regex = fields.List(fields.String())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._process = None
        self._pid = None
        self._cmd_path = None
        self.__tmux_window = None

    def reset(self):
        self._process = None
        self._pid = None

    @property
    def pid(self):
        if not self._pid:
            pids = j.sals.process.get_pids(f"startupcmd_{self.instance_name}")
            if pids:
                self._pid = pids[0]
        return self._pid

    @property
    def cmd_path(self):
        if not self._cmd_path:
            self._cmd_path = j.sals.fs.join_paths(j.core.dirs.VARDIR, "cmds", f"{self.instance_name}.sh")
            j.sals.fs.mkdirs(j.sals.fs.dirname(self._cmd_path))
        return self._cmd_path

    @pid.setter
    def pid(self, pid):
        self._pid = pid

    @property
    def process(self):
        if not self._process:
            if self.pid:
                self._process = j.sals.process.get_process_object(self.pid, die=False)
                if not self._process:
                    self.pid = None
            else:
                processes = self._get_processes_by_port_or_filter()
                if len(processes) == 1:
                    self._process = processes[0]
        return self._process

    @property
    def _tmux_window(self):
        if self.executor.value == Executor.TMUX.value:
            if self.__tmux_window is None:
                self.__tmux_window = j.core.executors.tmux.get_js_window(self.instance_name)
        return self.__tmux_window

    def _get_processes_by_port_or_filter(self):
        """Uses object properties to find the corresponding process(es)

        Returns:
            list: All processes that matched
        """

        pids_done = []
        result = []

        def _add_to_result(process):
            if process and process.pid not in pids_done:
                result.append(process)
                pids_done.append(process.pid)

        for port in self.ports:
            try:
                process = j.sals.process.get_process_by_port(port)
            except Exception:
                continue

            _add_to_result(process)

        for process_string in self.process_strings:
            for pid in j.sals.process.get_filtered_pids(process_string):
                process = j.sals.process.get_process_object(pid, die=False)
                _add_to_result(process)

        for pid in j.sals.process.get_pids_filtered_by_regex(self.process_strings_regex):
            process = j.sals.process.get_process_object(pid, die=False)
            _add_to_result(process)

        #  We return all processes which match
        return result

    def _kill_processes_by_port_or_filter(self):
        """Kills processes that matches object properties
        """
        processes = self._get_processes_by_port_or_filter()
        self._kill_processes(processes)

    def _kill_processes(self, processes):
        """Kill processes

        Args:
            processes (list): List of processes
        """
        for process in processes:
            try:
                process.kill()
            except NoSuchProcess:
                pass  # already killed

    def _soft_kill(self):
        """Kills the poocess using `stop_cmd`

        Returns:
            bool: True if was killed
        """
        if self.stop_cmd:
            cmd = j.tools.jinja2.render_template(template_text=self.stop_cmd, args=self._get_data())
            exit_code, _, _ = j.sals.process.execute(cmd, die=False)
            self.reset()
            return exit_code == 0
        elif self.process:
            try:
                self.process.terminate()
                return True
            except Exception:
                pass
        return False

    def _hard_kill(self):
        """Force Kills the process
        """
        if self.process:
            self._kill_processes([self.process])
            self.reset()

        self._kill_processes_by_port_or_filter()

        if self.executor.value == Executor.TMUX.value:
            self._tmux_window.kill_window()
            self.__tmux_window = None

    def stop(self, force=True, wait_for_stop=True, die=True, timeout=None):
        """Stops the running command

        Args:
            force (bool, optional): If True will force kill the process. Defaults to True.
            wait_for_stop (bool, optional): If True will wait until process is stopped. Defaults to True.
            die (bool, optional): If True will raise if timeout is exceeded for stop. Defaults to True.
            timeout (int, optional): Timeout for stop wait.If not set will use `timeout` property. Defaults to None.
        """

        timeout = timeout or self.timeout

        if self.is_running():
            if self._soft_kill():
                self.wait_for_stop(die=False, timeout=timeout)

        if force:
            self._hard_kill()

        if wait_for_stop:
            self.wait_for_stop(die=die, timeout=timeout)
        j.sals.process.execute(f"rm {self.cmd_path}", die=False)

    def is_running(self):
        """Checks if startup cmd is running. Will use `check_cmd` property if defined or check based on objet properties

        Returns:
            bool: True if it is running
        """
        if self.check_cmd:
            exit_code, _, _ = j.sals.process.execute(self.check_cmd, die=False)
            return exit_code == 0

        self.reset()
        if self.process:
            return self.process.is_running()
        return self._get_processes_by_port_or_filter() != []

    def _wait(self, for_running, die, timeout):
        """Wait for either start or stop to finishes

        Args:
            for_running (bool): Whether to check if it is running or stopped.
            die (bool, optional): If True will raise if timeout is exceeded for stop. Defaults to True.
            timeout (int, optional): Timeout for wait operation. Defaults to None.

        Raises:
            j.exceptions.Timeout: If timeout is exceeded.
        """
        end = j.data.time.now().timestamp + timeout

        while j.data.time.now().timestamp < end:
            if self.is_running() == for_running:
                break
            time.sleep(0.05)
        else:
            if die:
                raise j.exceptions.Timeout(f"Wait operation exceeded timeout: {timeout}")

    def wait_for_stop(self, die=True, timeout=10):
        """Wait for stop to finishes

        Args:
            die (bool, optional): If True will raise if timeout is exceeded for stop. Defaults to True.
            timeout (int, optional): Timeout for wait operation. Defaults to None.

        Raises:
            j.exceptions.Timeout: If timeout is exceeded.
        """
        self._wait(False, die, timeout)

    def wait_for_running(self, die=True, timeout=10):
        """Wait for start to finishes

        Args:
            die (bool, optional): If True will raise if timeout is exceeded for stop. Defaults to True.
            timeout (int, optional): Timeout for wait operation. Defaults to None.

        Raises:
            j.exceptions.Timeout: If timeout is exceeded.
        """
        self._wait(True, die, timeout)

    def start(self):
        """Starts the process
        """
        if self.is_running():
            return

        if not self.start_cmd:
            raise j.exceptions.Value("please make sure start_cmd has been set")

        if "\n" in self.start_cmd.strip():
            command = self.start_cmd
        else:
            template_script = """
            set +ex
            {% for key,val in env.items() %}
            export {{key}}='{{val}}'
            {% endfor %}

            mkdir -p {{path}}
            cd {{path}}
            bash -c \"exec -a startupcmd_{{name}} {{start_cmd}}\"

            """

            script = j.tools.jinja2.render_template(
                template_text=template_script,
                env=self.env,
                path=self.path,
                start_cmd=self.start_cmd,
                name=self.instance_name,
            )
            j.sals.fs.write_file(self.cmd_path, script)
            j.sals.fs.chmod(self.cmd_path, 0o770)
            command = f"sh {self.cmd_path}"

        if self.executor.value == Executor.FOREGROUND.value:
            j.sals.process.execute(command)
        elif self.executor.value == Executor.TMUX.value:
            self._tmux_window.attached_pane.send_keys(command)

        self.wait_for_running(die=True, timeout=self.timeout)
