"""This module execute process on system and manage them
for example
```
#to create a process
rc, out, err = j.sals.process.execute("ls", cwd="/tmp", showout=True)
#this executes ls command on dir "/tmp" showing output from stdout
#rc -> contains exit status
#out -> the actual output
#err -> in case an error happened this var will contains the error msg

j.sals.process.is_active(10022)
#checks if a process with this pid is active or not

j.sals.process.kill(10022, sig=signal.SIGTERM.value)
#kill a process with pid 10022 with SIGTERM

j.sals.process.get_pid_by_port(8000)
#gets pid of the process listenning on port 8000
```
"""


import math
import os
import os.path
import re
import signal
import time
from collections import defaultdict
import psutil
import socket
from jumpscale.loader import j
import subprocess


def execute(
    cmd,
    showout=False,
    cwd=None,
    shell="/bin/bash",
    timeout=600,
    asynchronous=False,
    env=None,
    replace_env=False,
    die=False,
):
    """Execute a command.

    Accepts command as a list too, with auto-escaping.

    Args:
        cmd (str/list[str]): Command to be executed, e.g. "ls -la" or ["ls", "-la"]
        showout (bool, optional): Whether to show stdout of the command or not. Defaults to False.
        cwd (str, optional): Path to `cd` into before running command. Defaults to None.
        shell (str, optional): Specify a working directory for the command. Defaults to "/bin/bash".
        timeout (int, optional): Timeout before kill the process. Defaults to 600.
        asynchronous (bool, optional): Whether to execute in asynchronous mode or not. Defaults to False.
        env (dict, optional): Add environment variables here. Defaults to None.
        replace_env (bool, optional): Whether to replace the entire environment with env. Defaults to False.
        die (bool, optional): Whether to raise exception if command failed or not. Defaults to False.

    Returns:
        tuple: tuple[return_code: int, stdout: str, stderr: str]
    """
    return j.core.executors.run_local(
        cmd=cmd,
        hide=not showout,
        cwd=cwd,
        shell=shell,
        timeout=timeout,
        asynchronous=asynchronous,
        env=env or {},
        replace_env=replace_env,
        warn=not die,
    )


def is_alive(pid):
    """Check whether the given PID exists in the current process list.

    Args:
        pid (int): Process ID (PID) to be checked.

    Returns:
        bool: True if the given PID exists in the current process list, False otherwise.
    """
    return psutil.pid_exists(pid)


def is_installed(cmd):
    """Checks if a specific command is available on system e.g. curl.

    Args:
        cmd (str): Command to be checked.

    Returns:
        bool: True if command is available, False otherwise.
    """
    rc, _, _ = execute(f"which {cmd}", die=False)
    return rc == 0


def kill(proc, sig=signal.SIGTERM, timeout=5, sure_kill=False):
    """Kill a process with a specified signal.

    Args:
        proc (int/psutil.Process): Target process ID (PID) or psutil.Process object.
        sig (signal, optional): See signal module constants. Defaults to signal.SIGTERM.
        timeout (int, optional): How long to wait for a process to terminate (seconds) before raise exception\
            or, if sure_kill=True, send a SIGKILL. Defaults to 5.
        sure_kill (bool, optional): Whether to fallback to SIGKILL if the timeout exceeded for the terminate operation or not. Defaults to False.

    Raises:
        j.exceptions.Runtime: In case killing the process failed.
        j.exceptions.Permission: In case the permission to perform this action is denied.

    Returns:
        None
    """
    try:
        if isinstance(proc, int):
            proc = get_process_object(proc)
        if proc.status() == psutil.STATUS_ZOMBIE:
            return True
        proc.send_signal(sig)
        # Wait for a process to terminate
        # If PID no longer exists return None immediately
        # If timeout exceeded and the process is still alive raise TimeoutExpired exception
        proc.wait(timeout=timeout)
        return True  # XXX only to pass current tests
    except psutil.TimeoutExpired as e:
        # timeout expires and process is still alive.
        if sure_kill and sig != signal.SIGKILL and os.name != "nt":
            # SIGKILL not supported in windows
            # If a process gets this signal it must quit immediately and will not perform any clean-up operations
            proc.kill()
            # TODO we can use timeout and catching TimeoutExpired again in case the process in an uninterruptible sleep
            try:
                proc.wait(1)
            except psutil.TimeoutExpired as e:
                if proc.status() == psutil.STATUS_ZOMBIE:
                    return True
                raise j.exceptions.Runtime(f"Could not kill process with pid {proc.pid}, {proc.status()}") from e
            return True  # XXX only to pass current tests
        else:
            raise j.exceptions.Runtime(f"Could not kill process with pid {proc.pid}, {proc.status()}") from e
    except psutil.AccessDenied as e:
        # permission to perform an action is denied
        raise j.exceptions.Permission("Permission to perform this action is denied!") from e
    except (psutil.ZombieProcess, psutil.NoSuchProcess):
        # Process no longer exists or Zombie (already dead)
        pass


def ps_find(process_name):
    """Check if there is any running process that match the given name.

    Args:
        process_name (str): The target process name. will match against against Process.name(),\
            Process.exe() and Process.cmdline()

    Returns:
        bool: True if process is found, False otherwise.
    """
    return len(get_pids(process_name, limit=1)) == 1


def kill_all(process_name, sig=signal.SIGKILL):
    """Kill all processes that match 'process_name'.

    Args:
        process_name (str): The target process name
        sig (signal, optional): See signal module constants. Defaults to signal.SIGKILL
    """
    # XXX kill default to SIGTERM while kill_all default to SIGKILL (inconsistency)?
    # XXX almost like kill_process_by_name
    kill_process_by_name(process_name, sig)


def get_pids_filtered_sorted(filterstr, sortkey=None):
    """Get pids of process by a filter string and optionally sort by sortkey

    Arguments:
        filterstr {[str]} -- filter string.

    Keyword Arguments:
        sortkey {[str]} -- sort key for ps command (default: {None})
        sortkey can be one of the following:
        %cpu           cpu utilization of the process in
        %mem           ratio of the process's resident set size  to the physical memory on the machine, expressed as a percentage.
        cputime        cumulative CPU time, "[DD-]hh:mm:ss" format.  (alias time).
        egid           effective group ID number of the process as a decimal integer.  (alias gid).
        egroup         effective group ID of the process.  This will be the textual group ID, if it can be obtained and the field width permits, or a decimal representation otherwise.  (alias group).
        euid           effective user ID (alias uid).
        euser          effective user name.
        gid            see egid.  (alias egid).
        pid            a number representing the process ID (alias tgid).
        ppid           parent process ID.
        psr            processor that process is currently assigned to.
        start_time     starting time or date of the process.


    Returns:
        [list(int)] -- processes pids
    """
    if sortkey is not None:
        cmd = "ps aux --sort={sortkey} | grep '{filterstr}'".format(filterstr=filterstr, sortkey=sortkey)
    else:
        cmd = "ps ax | grep '{filterstr}'".format(filterstr=filterstr)
    rc, out, err = execute(cmd)
    # print out
    found = []
    for line in out.split("\n"):
        if line.find("grep") != -1 or line.strip() == "":
            continue
        if line.strip() != "":
            if line.find(filterstr) != -1:
                line = line.strip()
                if sortkey is not None:
                    found.append(int([x for x in line.split(" ") if x][1]))
                else:
                    found.append(int(line.split(" ")[0]))
    return found


def get_filtered_pids(filterstr, excludes=None):
    """Get pids filtered by filterstr and execludes

    Arguments:
        filterstr {str} -- filter string.

    Keyword Arguments:
        excludes {list(str)} -- execlude list (default: {None})

    Returns:
        [list(int)] -- pids
    """
    excludes = excludes or []
    cmd = "ps ax | grep '%s'" % filterstr
    rc, out, err = j.core.executors.run_local(cmd)
    # print out
    found = []

    def checkexclude(c, excludes):
        for item in excludes:
            c = c.lower()
            if c.find(item.lower()) != -1:
                return True
        return False

    for line in out.split("\n"):
        if line.find("grep") != -1 or line.strip() == "":
            continue
        if line.strip() != "":
            if line.find(filterstr) != -1:
                line = line.strip()
                if not checkexclude(line, excludes):
                    # print "found pidline:%s"%line
                    found.append(int(line.split(" ")[0]))
    return found


def get_pids_filtered_by_regex(regex_list, excludes=None):
    """get pids of a process filtered by Regex list

    Arguments:
        regex_list {list(str)} -- list of regex expressions

    Keyword Arguments:
        excludes {list(str)} -- list of excludes (default: {None})

    Returns:
        [list(int)] -- list of pids
    """
    excludes = excludes or []
    res = []
    for process in psutil.process_iter():
        try:
            cmdline = process.cmdline()
        except psutil.NoSuchProcess:
            cmdline = None
        except psutil.AccessDenied:
            cmdline = None
        if cmdline:
            name = " ".join(cmdline)
            for r in regex_list:
                if name.strip() != "" and re.match(r, name):
                    res.append(process.pid)
    return res


def check_start(cmd, filterstr, n_instances=1, retry=1):
    """Run command (possibly multiple times) and check if it is started based on filterstr

    Args:
        cmd (str/list): Command to be executed.
        filterstr (str): Filter string. will match against against Process.name(),\
            Process.exe() and Process.cmdline()
        n_instances (int, optional): Number of needed instances. Defaults to 1.
        retry (int, optional): Number of retries to execute the command and check. Defaults to 1.

    Raises:
        j.exceptions.Runtime: will be raised if we didn't reach number of required instances.
    """
    for i in range(retry):
        if isinstance(cmd, str):
            cmd = cmd.split()
        proc = psutil.Popen(cmd, close_fds=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        # print(cmd)
        # print(proc.cmdline())
        # print(f'pid: {proc.pid}')
        # print(f'status: {proc.status()}')
        # print(f'name: {proc.name()}')
        # print(f'exe: {proc.exe()}')
        # print(f'children:{proc.children(recursive=True)}')
        # print(f'parent: {proc.parents()}')
        try:
            rc = proc.wait(timeout=1)  # makesure the process is stable
            # print(f'rc: {rc}')
            if rc == 0:  # executing the process succeeded but exited immediately!
                pass
            else:
                pass  # the process exited with error
        except psutil.TimeoutExpired:
            pass  # still running
        # TODO check based on command
        if check_running(filterstr, min=n_instances):
            return True  # XXX should remove? None
        else:
            continue
    raise j.exceptions.Runtime("could not start the required number of instances.")


def check_stop(cmd, filterstr, retry=1, n_instances=0):
    """Executes a stop command (possibly multiple times) and check if it is already stopped based on filterstr

    Args:
        cmd (str): Command to be executed.
        filterstr (str): Filter string.
        retry (int, optional): Number of retries. Defaults to 1.
        n_inst (int, optional): Number of instances after stop. Defaults to 0.

    Raises:
        j.exceptions.Runtime: if number of instances not matched
    """

    for i in range(retry):
        if isinstance(cmd, str):
            cmd = cmd.split()
        proc = psutil.Popen(cmd, close_fds=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            rc = proc.wait(timeout=5)  # makesure the process is stable
            # print(f'rc: {rc}')
            if rc == 0:
                pass  # executing the process succeeded but exited immediately!
            else:
                pass  # the process exited with error
        except psutil.TimeoutExpired:
            pass  # still running
        found = get_pids(filterstr)
        if len(found) == n_instances:
            return True  # should remove? None
        else:
            continue
    raise j.exceptions.Runtime(f"could not stop {cmd}, found {len(found)} of instances instead of {n_instances}")


def get_pids(process_name, match_predicate=None, limit=0, _alt_source=None):
    """Return a list of processes ID(s) matching 'process_name'.

    Function will check string against Process.name(), Process.exe() and Process.cmdline()

    Args:
        process_name (str): The target process name
        match_predicate (callable, optional): Function that does matching between\
            found processes and the targeted process, the function should accept\
            two arguments and return a boolean. Defaults to None.
        limit (int, optional): If not equal to 0, function will return as fast as the number\
            of PID(s) found become equal to `limit` value.
        _alt_source(callable or iterable, optional): Can be used to specify an alternative source\
            of the psutil.Process objects to match against.
            ex: get_user_processes func, or get_similar_processes.
            if not specified, psutil.process_iter will be used. Defaults to None.

    Returns:
        list[int]: list of PID(s)
    """
    # default match predicate
    def default_predicate(target, given):
        return target.strip().lower() == given.lower()

    match_predicate = match_predicate or default_predicate

    pids = []
    for proc in psutil.process_iter(["name", "exe", "cmdline"]):
        try:
            if (
                match_predicate(process_name, proc.info["name"])
                or proc.info["exe"]
                and match_predicate(process_name, os.path.basename(proc.info["exe"]))
                or proc.info["cmdline"]
                and match_predicate(process_name, os.path.basename(proc.info["cmdline"][0]))
            ):
                pids.append(proc.pid)
                # return early if no need to iterate over all running process
                if limit and len(pids) == limit:
                    return pids
        except (psutil.ZombieProcess, psutil.AccessDenied, psutil.NoSuchProcess):
            pass
    return pids


def get_my_process():
    """Get psutil.Process object of the current process.

    Returns:
        (psutil.Process): psutil.Process object of the current process.
    """
    return get_process_object(os.getpid())


def get_process_object(pid, die=True):
    """Get psutil.Process object of a given process ID (PID).

    Args:
        pid (int): Process ID (PID) to get
        die (bool, optional): Whether to raise an exception if no process with the given PID is found in the \
            current process list or not. Defaults to True.

    Raises:
        psutil.NoSuchProcess: If process with the given PID is not found and die set to True.
        psutil.AccessDenied: If permission denied.

    Returns:
        psutil.Process or None: psutil.Process object if he given PID is found, None otherwise.
    """
    try:
        return psutil.Process(pid)
    except (psutil.ZombieProcess, psutil.AccessDenied, psutil.NoSuchProcess) as e:
        # when you query processess owned by another user, especially on macOS and Windows you may get AccessDenied exception
        if die:
            raise e
        else:
            return None


def get_user_processes(user):
    """Get all process for a specific user.

    Args:
        user (str): Te user name to match against.

    Yields:
        psutil.Process: psutil.Process object for all processes owned by `user`.
    """
    try:
        for process in psutil.process_iter():
            if process.username() == user:
                yield process
    except (psutil.AccessDenied, psutil.NoSuchProcess):
        pass


def kill_user_processes(user):
    """Kill all processes for a specific user.

    Args:
        user (str): The user name to match against.

    Returns:
        None
    """
    for proc in get_user_processes(user):
        # XXX should we use  sure_kill here ?
        kill(proc, sure_kill=True)


def get_similar_processes(target_proc=None):
    """Gets similar processes to current process, started with same command line and same options.

    Args:
        target_proc (int or psutil.Process, optional): pid, or psutil.Process object,\
             if None then pid for current process will be used. Defaults to None.
    Returns:
        list[psutil.Process] -- list of similar process
    """
    try:
        if target_proc is None:
            target_proc = get_my_process()
        elif isinstance(target_proc, int):
            target_proc = get_process_object(target_proc)
        for proc in psutil.process_iter(["name", "cmdline"]):
            if proc.info["cmdline"] and target_proc.cmdline() and proc.info["cmdline"] == target_proc.cmdline():
                yield proc
    except (psutil.AccessDenied, psutil.NoSuchProcess):
        pass


def check_running(process_name, min=1):
    """Check if there are a specific number of running processes that match the given name.

    Function will check string against Process.name(), Process.exe() and Process.cmdline().

    Args:
        process_name (str): the target process name
        min (int, optional): min number of instances required to be running. Defaults to 1.

    Returns:
        bool: true if process is running, otherwise False
    """
    pids = get_pids(process_name, limit=min)
    return len(pids) == min


def check_process_for_pid(pid, process_name):
    """Check whether a given pid actually does belong to a given process name.

    Args:
        pid (int): Process ID
        process (str): String to match againset candidate processes name using equality operator

    Returns:
        bool: True if process_name matched process name of the pid, False otherwise.
    """
    try:
        proc = psutil.Process(pid)
        return proc.name() == process_name
    except (psutil.AccessDenied, psutil.NoSuchProcess):
        return False


def set_env_var(var_names, var_values):
    """Set the value of the environment variables {varnames}. Existing variable are overwritten

    Args:
        var_names list[str]: A list of the names of all the environment variables to set
        varvalues list[str]: A list of all values for the environment variables
    Raises:
        j.exceptions.RuntimeError: if error happened during setting the environment variables
    """
    try:
        for i in range(len(var_names)):
            os.environ[var_names[i]] = str(var_values[i]).strip()
    except Exception as e:
        raise j.exceptions.RuntimeError(e)


def get_pid_by_port(port):
    """Returns pids of the process that is listening on the given port

    Arguments:
        port (int) -- port number

    Returns:
        int -- pid of process that listen on that port
    """

    process = get_process_by_port(port)
    if process is None:
        return []
    return process.pid


def kill_process_by_name(process_name, sig=signal.SIGTERM, match_predicate=None, timeout=5, sure_kill=False):
    """Kill all processes that match 'process_name'.

    Args:
        process_name (str): The target process name.
        sig (signal, optional): See signal module constants. Defaults to signal.SIGKILL
        match_predicate (callable, optional): Function that does matching between\
            found processes and the targeted process, the function should accept\
            two arguments and return a boolean. Defaults to None.
    """
    pids = get_pids(process_name, match_predicate=match_predicate)
    for pid in pids:
        kill(pid, sig, timeout=timeout, sure_kill=sure_kill)


def kill_process_by_port(port):
    """Kill process by port

    Arguments:
        port (int) -- port number
    """
    port = int(port)
    pid = get_pid_by_port(port)
    if pid:
        return kill(pid)


def is_port_listening(port, ipv6=False):
    """Check if the port is being used by any process

    Args:
        port (int): Port number

    Returns:
        bool: True if port is used, False otherwise.
    """
    # XXX only support ipv4, also it apparently used to pick a free port, any way using nettools is preferred
    from jumpscale.sals import nettools

    ip6 = "::"
    ip4 = "0.0.0.0"
    return nettools.tcp_connection_test(ip6 if ipv6 else ip4, port, timeout=5)


def get_process_by_port(port):
    """Returns the full name of the process that is listening on the given port

    Arguments:
        port (int) -- the port for which to find the command

    Raises:
        Runtime Error if the process is not accessible by the user

    Returns:
        [psutil.Process] -- process object
        None -- No process found
    """
    # XXX should we check against ESTABLISHED status?
    pcons = [proc for proc in psutil.net_connections() if proc.laddr.port == port and proc.status == "LISTEN"]
    if pcons:
        pid = pcons[0].pid
        if not pid:
            raise j.exceptions.Runtime("No pid found maybe permission denied on the process")
        return psutil.Process(pid)


def get_defunct_processes():
    """Gets defunct (zombie) processes.

    Returns:
        list[int]: List of processes ID(s).
    """
    zombie_pids = []
    for proc in psutil.process_iter():
        try:
            if proc.status() == psutil.STATUS_ZOMBIE:
                zombie_pids.append(proc.pid)
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
    return zombie_pids


def get_processes():
    """
    get an interator for all running processes

    Yields:
        generator: for all processes
    """
    yield from psutil.process_iter()


def get_processes_info():
    """
    Get information for top 25 running processes sorted by memory usage

    Returns:
        [list(dict)] -- list of processes info
    """
    processes_list = []
    for proc in get_processes():
        try:
            # Fetch process details as dict
            pinfo = proc.as_dict(attrs=["pid", "name", "username"])
            pinfo["rss"] = proc.memory_info().rss / (1024 * 1024)
            pinfo["ports"] = []
            try:
                connections = proc.connections()
            except psutil.Error:
                continue
            if connections:
                for conn in connections:
                    pinfo["ports"].append({"port": conn.laddr.port, "status": conn.status})
            # Append dict to list
            processes_list.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    processes_list = sorted(processes_list, key=lambda procObj: procObj["rss"], reverse=True)
    return processes_list[:25]


def get_ports_mapping(status=psutil.CONN_LISTEN):
    """
    get a mapping for process to ports with a status filter

    it will skip any process in case of errors (e.g. permission error)

    example:

    ```python
    j.sals.process.get_ports_mapping(psutil.CONN_ESTABLISHED)
    ```

    or

    ```
    j.sals.process.get_ports_mapping("ESTABLISHED")
    ```

    Args:
        status (psutil.CONN_CONSTANT): `psutil` CONN_* constant as a filter. Defaults to psutil.CONN_LISTEN.

    Returns:
        defaultdict: a mapping between process and ports
    """
    ports = defaultdict(list)

    for process in get_processes():
        try:
            connections = process.connections()
        except psutil.Error:
            continue

        if connections:
            for conn in connections:
                if conn.status == status:
                    ports[process].append(conn.laddr.port)

    return ports


def get_memory_usage():
    """
    Get memory status

    Returns:
        dict -- memory status info
    """
    memory_usage = {}
    memory_data = dict(psutil.virtual_memory()._asdict())
    memory_usage["total"] = math.ceil(memory_data.get("total") / (1024 * 1024 * 1024))
    memory_usage["used"] = math.ceil(memory_data.get("used") / (1024 * 1024 * 1024))
    memory_usage["percent"] = memory_data.get("percent")
    return memory_usage


def get_environ(pid):
    """Gets env vars for a specific process based on pid

    Arguments:
        pid (int) -- process pid

    Returns:
        [dict] -- dict of env variables
    """
    pid = int(pid)
    return psutil.Process(pid).environ()


def in_docker():
    """will check if we are in a docker

    Returns:
        Bool: True if in docker - False if not
    """
    rc, out, _ = j.sals.process.execute("cat /proc/1/cgroup", die=False, showout=False)
    if rc == 0 and "/docker/" in out:
        return True
    return False


def in_host():
    """will check if we are in a host

    Returns:
        Bool: True if in host - False if not
    """
    return not in_docker()
