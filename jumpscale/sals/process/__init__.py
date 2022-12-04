"""This module execute process on system and manage them

below are some examples of the functions included in this module (not all inclusive.):

Examples:
    ```
    >>> from jumpscale.loader import j
    >>> import signal

    #to create a process
    >>> rc, out, err = j.sals.process.execute("ls", cwd="/tmp", showout=True)
    # this executes ls command on dir "/tmp" showing output from stdout
    # rc -> contains exit status
    # out -> the actual output
    # err -> in case an error happened this var will contains the error msg

    # checks if a process with this pid is exists in the current process list
    >>> j.sals.process.is_alive(10022)

    # Checks if a specific command is available on the system
    >>> j.sals.process.is_installed('top')

    # kill a process with pid 10022 with SIGTERM
    >>> j.sals.process.kill(10022)

    # kill a process with pid 10022 with SIGTERM, wait 3 seconds for it to disappear, then if still alive kill it with SIGKILL
    >>> j.sals.process.kill(10022, timeout=3, sure_kill=True)

    # Check if there is any running process that match the given name.
    >>> j.sals.process.ps_find('python3')

    # gets pid of the process listenning on port TCP 8000 ipv4 localhost address
    >>> j.sals.process.get_pid_by_port(8000)

    # gets pid of the process listenning on port UDP 8000 ipv6 localhost address
    >>> j.sals.process.get_pid_by_port(8000, ipv6=True, udp=True)

    # Returns the psutil.Process object that is listening on the given port
    >>> j.sals.process.get_process_by_port(8000, ipv6=True, udp=True)

    # Get pids of process by a filter string and sort by cpu utilization descendingly
    >>> j.sals.process.get_pids_filtered_sorted('chrome', sort='%cpu', desc=True)

    # Return a list of processes ID(s) matching the given name.
    >>> j.sals.process.get_pids('code')

    # Return a list of processes ID(s) matching the given name, including the result of matching againest the full command line.
    >>> j.sals.process.get_pids('http.server', full_cmd_line=True)

    # Return a list of processes ID(s) matching the given name, including any zombie processes
    >>> j.sals.process.get_pids('python3', include_zombie=False)

    # get processes info about top 3 processes which consumed the most memory
    >>> j.sals.process.get_processes_info(limit=3)

    # get processes info about top 3 processes which consumed the most cpu time
    >>> j.sals.process.get_processes_info(sort='cpu_time', limit=3)

    # get processes info about last process started
    >>> j.sals.process.get_processes_info(sort='create_time', limit=1)

    # get processes info sorted by pid ascending limited to 10 processes
    >>> j.sals.process.get_processes_info(sort='pid', limit=10, desc=False)

    # Kill a process and its children (including grandchildren) with SIGTERM and fallback to SIGKILL when needed
    >>> j.sals.process.kill_proc_tree(20778, sure_kill=True)

    # send SIGTERM to all processes spawned by a given process, but leave the process itself.
    >>> j.sals.process.kill_proc_tree(20778, include_parent=False)

    # Terminate a list of processes with a given list of pids, fallback to SIGKILL after 1 seconds.
    >>> j.sals.process.kill_all_pids([3067, 7888, 10221], timeout=1, sure_kill=True)

    # terminate a process that listen to a given tcp port on ipv4 address
    >>> j.sals.process.kill_process_by_port(8000)

    # terminate a process that listen to a given udp port on ipv6 address, fallback to SIGKILL after 3 sec
    >>> j.sals.process.kill_process_by_port(8000, udp=True, ipv6=True, timeout=3, sure_kill=True)

    # Terminate all processes owned by a given user name, fallback to SIGKILL when needed
    >>> j.sals.process.kill_user_processes('sameh', sure_kill=True)
    ```
"""


import math
import os
import re
import shlex
import signal
import subprocess
import time
from collections import defaultdict

import psutil
from jumpscale.loader import j


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
        cmd (str or list of str): Command to be executed, e.g. "ls -la" or ["ls", "-la"]
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
        proc (int or psutil.Process): Target process ID (PID) or psutil.Process object.
        sig (signal, optional): See signal module constants. Defaults to signal.SIGTERM.
        timeout (int, optional): How long to wait for a process to terminate (seconds) before raise exception
            or, if sure_kill=True, send a SIGKILL. Defaults to 5.
        sure_kill (bool, optional): Whether to fallback to SIGKILL if the timeout exceeded for the terminate operation or not. Defaults to False.

    Raises:
        j.exceptions.Runtime: In case killing the process failed.
        j.exceptions.Permission: In case the permission to perform this action is denied.
    """
    try:
        if isinstance(proc, int):
            proc = get_process_object(proc, die=True)
        if proc.status() == psutil.STATUS_ZOMBIE:
            return
        proc.send_signal(sig)
        # Wait for a process to terminate
        # If PID no longer exists return None immediately
        # If timeout exceeded and the process is still alive raise TimeoutExpired exception
        proc.wait(timeout=timeout)
        # the process with PID {proc.pid} was terminated with sig {sig}
    except psutil.TimeoutExpired as e:
        # timeout expires and process is still alive.
        if sure_kill and sig != signal.SIGKILL and os.name != "nt":
            # SIGKILL not supported in windows
            # If a process gets this signal it must quit immediately and will not perform any clean-up operations
            proc.kill()
            # SIGKILL signal sent
            try:
                proc.wait(1)
                # the process with PID {proc.pid} was terminated with sig {signal.SIGKILL}
            except psutil.TimeoutExpired as e:
                if proc.status() == psutil.STATUS_ZOMBIE:
                    # the process with PID: {proc.pid} becomes a zombie and should be considered a dead.
                    return
                # the process may be in an uninterruptible sleep
                j.logger.warning(f"Could not kill the process with pid: {proc.pid} with {sig}. Timeout: {timeout}")
                raise j.exceptions.Runtime(f"Could not kill process with pid {proc.pid}, {proc.status()}") from e
        else:
            raise j.exceptions.Runtime(f"Could not kill process with pid {proc.pid}") from e
    except psutil.AccessDenied as e:
        # permission to perform an action is denied
        raise j.exceptions.Permission("Permission to perform this action is denied!") from e
    except psutil.NoSuchProcess:
        # Process no longer exists or Zombie (already dead)
        pass


def ps_find(process_name):
    """Check if there is any running process that match the given name.

    Args:
        process_name (str): The target process name. will match against against Process.name(), Process.exe() and Process.cmdline()

    Returns:
        bool: True if process is found, False otherwise.
    """
    return len(get_pids(process_name, limit=1)) == 1


def get_pids_filtered_sorted(filterstr, sortkey=None, desc=False):
    """Get pids of process by a filter string and optionally sort by sortkey

    Args:
        filterstr (str): filter string.
        sortkey (str, optional): Defaults to None. (if no sortkey used it will sort by pid(s) in ascending order).
            sortkey can be one of the following:
            %cpu           cpu utilization of the process in
            %mem           ratio of the process's resident set size  to the physical memory on the machine, expressed as a percentage.
            cputime        cumulative CPU time, "[DD-]hh:mm:ss" format.  (alias time).
            egid           effective group ID number of the process as a decimal integer.  (alias gid).
            egroup         effective group ID of the process. This will be the textual group ID, if it can be obtained and the field width permits, or a decimal representation otherwise.  (alias group).
            euid           effective user ID (alias uid).
            euser          effective user name.
            gid            see egid. (alias egid).
            pid            a number representing the process ID (alias tgid).
            ppid           parent process ID.
            psr            processor that process is currently assigned to.
            start_time     starting time or date of the process.
        desc: (bool, optional): Whether to sort the processes in descending order or not(asc). Defaults to False (asc).

    Returns:
        list of int: list of the processes IDs
    """
    ps_to_psutil_map = {
        "%cpu": "cpu_percent",
        "%mem": "memory_percent",
        "cputime": "cpu_time",
        "psr": "cpu_num",
        "start_time": "create_time",
        "egid": "egid",
        "gid": "egid",
        "euid": "euid",
        "uid": "euid",
        "euser": "username",
        "pid": "pid",
        "ppid": "ppid",
    }
    if sortkey is None:  # mimic default ps commnad sorting behavior
        sortkey = "pid"
    # return pids from process objects
    return [p["pid"] for p in get_processes_info(sort=ps_to_psutil_map[sortkey], filterstr=filterstr, desc=desc)]


def get_filtered_pids(filterstr, excludes=None):
    """Get pids filtered by filterstr and excludes, matching against the full command line used to start the process.

    Args:
        filterstr (str): the String to filter based on.
        excludes (list[str]): exclude list. Defaults to None.

    Returns:
        list of int: List of the processes IDs
    """
    pids = []
    for proc in psutil.process_iter(["name", "cmdline"]):
        cmd_line = " ".join(proc.info["cmdline"])
        if proc.info["cmdline"] and filterstr in cmd_line:
            # found filter string: {filterstr} in command line: {cmd_line}
            if excludes:
                for exclude in excludes:
                    if exclude in cmd_line:
                        # we excluded this because it contain exclude string
                        break
                else:  # intended `for/else` meaning for loop finished normally with no break
                    pids.append(proc.pid)  # may yield proc instead
                continue
            else:
                pids.append(proc.pid)  # may yield proc instead
    # if pids is empty root could be needed
    return pids


def get_pids_filtered_by_regex(regex_list):
    """Get pids of a process filtered by Regex list, matching against the full command line used to start the process.

    Args:
        regex_list (list[str]): List of regex expressions.

    Returns:
        list of int: List of the processes IDs.
    """
    res = []
    for process in psutil.process_iter(attrs=["cmdline"]):
        if process.info["cmdline"]:
            cmdline = " ".join(process.info["cmdline"])
            for r in regex_list:
                if re.match(r, cmdline):
                    res.append(process.pid)
    return res


def check_start(cmd, filterstr, n_instances=1, retry=1, timeout=2, delay=0.5):
    """Run command (possibly multiple times) and check if it is started based on filterstr

    Args:
        cmd (str or list of str): Command to be executed.
        filterstr (str): Filter string. will match against against Process.name(), Process.exe() and Process.cmdline()
        n_instances (int, optional): Number of needed instances. Defaults to 1.
        retry (int, optional): Number of retries to execute the command and check. Defaults to 1.
        timout (int, optional): how long the function should wait for process to finish (first or parnet process started with the command)
        delay (int, optional): how long the function should delay the checking process after the process finished or timeout exceeded (in case the first process started another one).

    Raises:
        j.exceptions.Runtime: will be raised if we didn't reach number of required instances.
    """
    for i in range(retry):
        if isinstance(cmd, str):
            args = shlex.split(cmd)
        proc = psutil.Popen(args, close_fds=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            rc = proc.wait(timeout)  # makesure the process is stable
            if rc != 0:  # executing the command succeeded but exited immediately!
                output, error_output = proc.communicate()
                j.logger.error(f"the start command exited with error: {error_output}")  # the process exited with error
        except psutil.TimeoutExpired:
            pass  # still running
        # wait extra delay to allow any subprocess spawned from the process we just started to finish
        # this may not needed in many cases
        time.sleep(delay)
        # TODO check based on command
        if check_running(filterstr, min=n_instances):
            # found at least {n_instances} instances using the filter string {filterstr}
            return
        else:
            # the required number of instances using the filter string {filterstr} not found yet!
            continue
    j.logger.error(f"could not start the required number of instances ({n_instances}) after {i} attempts.")
    raise j.exceptions.Runtime("could not start the required number of instances.")


def check_stop(cmd, filterstr, retry=1, n_instances=0, timeout=2, delay=0.5):
    """Executes a stop command (possibly multiple times) and check if it is already stopped based on filterstr

    Args:
        cmd (str): Command to be executed.
        filterstr (str): Filter string.
        retry (int, optional): Number of retries. Defaults to 1.
        n_inst (int, optional): Number of instances after stop. Defaults to 0.
        timout (int, optional): how long the function should wait for process to finish (first or parnet process started with the command)
        delay (int, optional): how long the function should delay the checking process after the process finished or timeout exceeded (in case the first process started another one).

    Raises:
        j.exceptions.Runtime: if number of instances not matched
    """

    for i in range(retry):
        if isinstance(cmd, str):
            args = shlex.split(cmd)
        proc = psutil.Popen(args, close_fds=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            rc = proc.wait(timeout)  # makesure the process is stable
            # print(f'rc: {rc}')
            if rc != 0:
                # the process exited with error
                output, error_output = proc.communicate()
                j.logger.warnnig(f"the stop command exited with error: {error_output}")
        except psutil.TimeoutExpired:
            # still running
            pass
        # wait extra delay to allow any subprocess spawned from the process we just started to finish
        # this may not needed in many cases
        time.sleep(delay)
        found = get_pids(filterstr)
        if len(found) == n_instances:
            # the required {n_instances} matching the instances found using the filter string: {filterstr}
            return
        else:
            # the required {n_instances} not matching the instances number found using the filter string: {filterstr} yet
            continue
    # could not match the required number of instances {n_instances} after {i} attempts.
    raise j.exceptions.Runtime(f"could not stop {cmd}, found {len(found)} of instances instead of {n_instances}")


def get_pids(process_name, match_predicate=None, limit=0, _alt_source=None, include_zombie=False, full_cmd_line=False):
    """Return a list of processes ID(s) matching a given process name.

    Function will check string against Process.name(), Process.exe() and Process.cmdline()

    Args:
        process_name (str): The target process name
        match_predicate (callable, optional): Function that does matching between found processes and the targeted process.
            the function should accept two arguments and return a boolean. Defaults to None.
        limit (int, optional): If not equal to 0, function will return as fast as the number of PID(s) found become equal to `limit` value.
        _alt_source(callable or iterable, optional): Can be used to specify an alternative source of the psutil.Process objects to match against.
            ex: get_user_processes func, or get_similar_processes.
            if not specified, psutil.process_iter will be used. Defaults to None.
        include_zombie (bool, optional): Whether to include pid for zombie proccesses or not. Defaults to False.
        full_cmd_line (bool, optional): The pattern is normally only matched against the process name.
            if full_cmd_line is set to True, the full command line is used. Defaults to False.

    Returns:
        list of int: List of the processes IDs.
    """
    # default match predicate
    def default_predicate(target, given):
        if isinstance(given, list):
            return target in given
        else:
            return target.strip().lower() == given.lower()

    default_processes_source = psutil.process_iter(["name", "exe", "cmdline"])

    match_predicate = match_predicate or default_predicate
    p_source = _alt_source or default_processes_source

    pids = []
    for proc in p_source:
        try:
            if not include_zombie and proc.status() == psutil.STATUS_ZOMBIE:
                # {proc.pid} is a zombie process, ignoring it
                continue

            candidates = [proc.info["name"]]
            if proc.info["exe"]:
                candidates.append(os.path.basename(proc.info["exe"]))
            if proc.info["cmdline"]:
                if full_cmd_line:
                    candidates.append(proc.info["cmdline"])
                else:
                    candidates.append(os.path.basename(proc.info["cmdline"][0]))

            if any([match_predicate(process_name, candidate) for candidate in candidates]):
                pids.append(proc.pid)
                # return early if no need to iterate over all running process
                if limit and len(pids) == limit:
                    return pids
        except psutil.Error:
            pass
    return pids


def get_my_process():
    """Get psutil.Process object of the current process.

    Returns:
        psutil.Process: Process object of the current process.
    """
    return get_process_object(os.getpid(), die=True)


def get_process_object(pid, die=False):
    """Get psutil.Process object of a given process ID (PID).

    Args:
        pid (int): Process ID (PID) to get
        die (bool, optional): Whether to raise an exception if no process with the given PID is found in the
            current process list or not. Defaults to False.

    Raises:
        psutil.NoSuchProcess: If process with the given PID is not found and die set to True.
        psutil.AccessDenied: If permission denied.

    Returns:
        psutil.Process or None: The Process object of the given PID if found, otherwise None, if die set to False.
    """
    try:
        return psutil.Process(pid)
    except (psutil.AccessDenied, psutil.NoSuchProcess) as e:
        # when you query processess owned by another user, especially on macOS and Windows you may get AccessDenied exception
        if die:
            raise e
        else:
            return None


def get_user_processes(user):
    """Get all process for a specific user.

    Args:
        user (str): The user name to match against.

    Yields:
        psutil.Process: process object for all processes owned by `user`.
    """
    try:
        for process in psutil.process_iter(["name", "exe", "cmdline"]):
            if process.username() == user:
                yield process
    except (psutil.AccessDenied, psutil.NoSuchProcess):
        pass


def kill_user_processes(user, sig=signal.SIGTERM, timeout=5, sure_kill=False):
    """Kill all processes for a specific user.

    Args:
        user (str): The user name to match against.
        sig (signal, optional): See signal module constants. Defaults to signal.SIGTERM.
        timeout (int, optional): How long to wait for a process to terminate (seconds) before raise exception or, if sure_kill=True, send a SIGKILL. Defaults to 5.
        sure_kill (bool, optional): Whether to fallback to SIGKILL if the timeout exceeded for the terminate operation or not. Defaults to False.

    Returns:
        list of psutil.Process): list of process objects that remain alive if any.
    """
    failed_processes = []
    for proc in get_user_processes(user):
        try:
            kill(proc, sig=sig, timeout=timeout, sure_kill=sure_kill)
        except (j.exceptions.Runtime, j.exceptions.Permission) as e:
            j.logger.exception("ignoring an exception that occurred while iterating over user processes", exception=e)
            failed_processes.append(proc)

    # making sure
    if failed_processes:
        gone, failed_processes = psutil.wait_procs(failed_processes, timeout=0)

    return failed_processes


def get_similar_processes(target_proc=None):
    """Gets similar processes to current process, started with same command line and same options.

    Args:
        target_proc (int or psutil.Process, optional): pid, or psutil.Process object.
            if None then pid for current process will be used. Defaults to None.

    Yields:
        psutil.Process: psutil.Process object for all processes similar to a given process.
    """
    try:
        if target_proc is None:
            target_proc = get_my_process()
        elif isinstance(target_proc, int):
            target_proc = get_process_object(target_proc, die=True)
        for proc in psutil.process_iter(["name", "exe", "cmdline"]):
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

    Such changes to the environment affect subprocesses started with os.system(), popen() or fork() and execv()

    Args:
        var_names (list of str): A list of the names of all the environment variables to set
        varvalues (list of str): A list of all values for the environment variables

    Raises:
        j.exceptions.RuntimeError: if error happened during setting the environment variables
    """
    # Note:
    # On some platforms, including FreeBSD and Mac OS X, setting environ may cause memory leaks.
    # https://docs.python.org/3/library/os.html?highlight=os%20environ#os.environ
    # Refer to the system documentation for putenv().
    for i in range(len(var_names)):
        os.environ[var_names[i]] = str(var_values[i]).strip()


def get_pid_by_port(port, ipv6=False, udp=False):
    """Returns the PID of the process that is listening on the given port

    Args:
        port (int): Port number to lookup for.
        ipv6 (bool, optional): Whether to search the connections that using ipv6 instead of ipv4. Defaults to False.
        udp (bool, optional): Whether to search the connections for UDP port instead of TCP. Defaults to False.

    Returns:
        int or None: PID for the proceses that listen on that port.
    """

    process = get_process_by_port(port, ipv6=ipv6, udp=udp)
    if process:
        return process.pid


def kill_process_by_name(process_name, sig=signal.SIGTERM, match_predicate=None, timeout=5, sure_kill=False):
    """Kill all processes that match 'process_name'.

    Args:
        process_name (str): The target process name.
        sig (signal, optional): See signal module constants. Defaults to signal.SIGKILL
        match_predicate (callable, optional): Function that does matching between\
            found processes and the targeted process, the function should accept\
            two arguments and return a boolean. Defaults to None.
        timeout (int, optional): How long to wait for a process to terminate (seconds) before raise exception\
            or, if sure_kill=True, send a SIGKILL. Defaults to 5.
        sure_kill (bool, optional): Whether to fallback to SIGKILL if the timeout exceeded for the terminate operation or not. Defaults to False.

    Returns:
        list of int: represents the IDs of the processes remaning alive if any.
    """
    pids = get_pids(process_name, match_predicate=match_predicate)
    failed_processes = []
    for pid in pids:
        try:
            kill(pid, sig, timeout=timeout, sure_kill=sure_kill)
        except (j.exceptions.Runtime, j.exceptions.Permission):
            failed_processes.append(pid)
    return failed_processes


def kill_all_pids(pids, sig=signal.SIGTERM, timeout=5, sure_kill=False):
    """Kill all processes with given pids.

    Args:
        pids (list of int): The target processes IDs.
        sig (signal, optional): See signal module constants. Defaults to signal.SIGKILL.
        timeout (int, optional): How long to wait for a process to terminate (seconds) before raise exception\
            or, if sure_kill=True, send a SIGKILL. Defaults to 5.
        sure_kill (bool, optional): Whether to fallback to SIGKILL if the timeout exceeded for the terminate operation or not. Defaults to False.


    Returns:
        list of int: represents the IDs of the processes remaning alive if any.
    """
    failed_processes = []
    for pid in pids:
        try:
            kill(pid, sig, timeout=timeout, sure_kill=sure_kill)
        except (j.exceptions.Runtime, j.exceptions.Permission):
            failed_processes.append(pid)
    return failed_processes


def kill_process_by_port(port, ipv6=False, udp=False, sig=signal.SIGTERM, timeout=5, sure_kill=False):
    """Kill process by port.

    Args:
        port (int): The port number.
        ipv6 (bool, optional): Whether to search the connections that using ipv6 instead of ipv4. Defaults to False.
        udp (bool, optional): Whether to search the connections for UDP port instead of TCP. Defaults to False.
        sig (signal, optional): See signal module constants. Defaults to signal.SIGTERM.
        timeout (int, optional): How long to wait for a process to terminate (seconds) before raise exception
            or, if sure_kill=True, send a SIGKILL. Defaults to 5.
        sure_kill (bool, optional): Whether to fallback to SIGKILL if the timeout exceeded for the terminate operation or not. Defaults to False.

    Raises:
        j.exceptions.Runtime: In case killing the process failed.
        j.exceptions.Permission: In case the permission to perform this action is denied.
    """
    proc = get_process_by_port(port, ipv6=ipv6, udp=udp)
    kill(proc, sig=sig, timeout=timeout, sure_kill=sure_kill)


def is_port_listening(port, ipv6=False):
    """Check if the TCP port is being used by any process

    Args:
        port (int): Port number
        ipv6 (bool, optional): Whether to ipv6 localhost address instead of ipv4 localhost address. Defaults to False.

    Returns:
        bool: True if port is used, False otherwise.
    """
    from jumpscale.sals import nettools

    ip6 = "::"
    ip4 = "0.0.0.0"
    return nettools.tcp_connection_test(ip6 if ipv6 else ip4, port, timeout=5)


def get_process_by_port(port, ipv6=False, udp=False):
    """Returns the psutil.Process object that is listening on the given port.

    Args:
        port (int): The port for which to find the process.
        ipv6 (bool, optional): Whether to search the connections that using ipv6 instead of ipv4. Defaults to False.
        udp (bool, optional): Whether to search the connections for UDP port instead of TCP. Defaults to False.

    Raises:
        j.exceptions.Runtime: pid is not retrievable.
        j.exceptions.NotFound: if the process is no longer exists.
        j.exceptions.Permission: if the process is not accessible by the user.

    Returns:
        psutil.Process: process object if found, otherwise None
    """
    for conn in psutil.net_connections():  # TODO use kind parameter
        try:
            # should we check against ESTABLISHED status?
            # connection.status For UDP and UNIX sockets this is always going to be psutil.CONN_NONE
            if (
                conn.laddr.port == port
                and conn.status in ["LISTEN", "NONE", "ESTABLISHED"]
                and (conn.family.name == "AF_INET6") == ipv6
                and (conn.type.name == "SOCK_DGRAM") == udp
            ):
                if conn.pid:
                    return psutil.Process(conn.pid)
                else:
                    raise j.exceptions.Runtime("pid is not retrievable, not root?")
        except psutil.NoSuchProcess:
            raise j.exceptions.NotFound("Process is no longer exists")
        except psutil.AccessDenied:
            raise j.exceptions.Permission("Permission denied")


def get_defunct_processes():
    """Gets defunct (zombie) processes.

    Returns:
        list of int: List of processes ID(s).
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
    """Get an interator for all running processes

    Yields:
        psutil.Process: for all processes running
    """
    yield from psutil.process_iter()


def get_processes_info(user=None, sort="mem", filterstr=None, limit=25, desc=True):
    """Get information for top running processes sorted by memory usage or CPU usage.

    Args:
        user ([type], optional): filter the processes by username. Defaults to None.
        sort (str, optional): sort processes by resource usage, Defaults to 'mem'.
            available option:
                'rss' and its alias 'mem': sort by processes which consumed the most memory (Resident Set Size).
                'cpu_times' and its alias 'cpu_time': sort by processes which consumed the most CPU time.
                'cpu_num': sort by the CPU number this process is currently running on.
                'cpu_percent': sort by a float representing the process CPU utilization as a percentage which can also\
                    be > 100.0 in case of a process running multiple threads on different CPUs.
                'memory_percent': sort py the process memory utilization, the process memory to total physical system memory as a percentage
                'create_time': the process creation time as a floating point number expressed in seconds since the epoch.
                'gids' and its alias 'egid': the effective group id of this process
                'uids' and its alias 'euid': the effective user id of this process
                'pid': sort by the process PID.
                'ppid': sort by the process parent PID
                'name': sort by the processes name
                'username': sort by the name of the user that owns the process.
                'status': sort by the current process status, one of the psutil.STATUS_* constants
        filterstr (str, optional): the string to match against process name or command used and filter the results based on.
        limit (int, optional): limit the results to specific number of processes, to disable set it to -1. Defaults to 25.
        desc (bool, optional): whether to sort the data returned in descending order or not. Defaults to True.

    Returns:
        dict: processes info as a dictionary
            available keys [
                    "cpu_num",
                    "cpu_percent",
                    "cpu_times",
                    "create_time",
                    "gids",
                    "memory_percent",
                    "name",
                    "pid",
                    "ppid",
                    "status",
                    "uids",
                    "username",
                    "rss",
                    "cpu_time",
                    "ports"
                ]
    """

    def _get_sort_key(procObj):
        if sort == "mem":
            return procObj["rss"]
        if sort == "cpu_times":
            return procObj["cpu_time"]
        elif sort in ["gids", "egid"]:
            return procObj["gids"].effective
        elif sort in ["uids", "euid"]:
            return procObj["uids"].effective
        else:
            try:
                return procObj[sort]
            except KeyError:
                j.logger.error(f"bad field name for sorting: {sort}")
                raise j.exceptions.Value(f"bad field name for sorting: {sort}")

    processes_list = []
    if not filterstr:
        if user:
            p_source = get_user_processes(user=user)
        else:
            p_source = get_processes()
    else:
        # it makes sense that get_pids func should returns list of psutil.Process objects instead of list of pids
        if user:
            p_source = map(get_process_object, get_pids(process_name=filterstr, _alt_source=get_user_processes(user)))
        else:
            p_source = map(get_process_object, get_pids(process_name=filterstr))
    for proc in p_source:
        if proc:  # in case a race condition happened, and get_process_object returned None
            try:
                # Fetch process details as dict
                pinfo = proc.as_dict(
                    attrs=[
                        "cpu_num",
                        "cpu_percent",
                        "cpu_times",
                        "create_time",
                        "gids",
                        "memory_percent",
                        "name",
                        "pid",
                        "ppid",
                        "status",
                        "uids",
                        "username",
                    ]
                )
                pinfo["rss"] = proc.memory_info().rss / (
                    1024 * 1024
                )  # the non-swapped physical memory a process has used in Mb
                pinfo["cpu_time"] = sum(pinfo["cpu_times"][:2])  # cumulative, excluding children and iowait
                pinfo["ports"] = []
                try:
                    connections = proc.connections()  # need root
                except (psutil.AccessDenied):
                    pass
                else:
                    if connections:
                        for conn in connections:
                            pinfo["ports"].append({"port": conn.laddr.port, "status": conn.status})
                # Append dict to list
                processes_list.append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                j.logger.exception(
                    "ignoring and logging an exception that occurred while iterating over system processes, not root?",
                    exception=e,
                )
                pass
    # sort the processes list by sort_key
    sorted_processes = sorted(processes_list, key=_get_sort_key, reverse=desc)[:limit]
    return sorted_processes


def get_ports_mapping(status=psutil.CONN_LISTEN):
    """Get a mapping for process to ports with a status filter

    It will skip any process in case of errors (e.g. permission error)

    Example:
        >>> from jumpscale.loader import j
        >>> import psutil
        >>> j.sals.process.get_ports_mapping(psutil.CONN_ESTABLISHED)
        >>> # or
        >>> j.sals.process.get_ports_mapping("ESTABLISHED")

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
    """Get memory status

    Returns:
        dict: Memory status info, available keys ('total', 'used', 'percent')
            'total': total physical memory in Gb (exclusive swap).
            'used': memory used in Gb, calculated differently depending on the platform and designed for informational purposes only.
                total - free does not necessarily match used.
            'percent': the percentage of used memory.
    """
    memory_usage = {}
    memory_data = dict(psutil.virtual_memory()._asdict())
    memory_usage["total"] = math.ceil(
        memory_data.get("total") / (1024 * 1024 * 1024)
    )  # total physical memory (exclusive swap).
    memory_usage["used"] = math.ceil(memory_data.get("used") / (1024 * 1024 * 1024))
    memory_usage["percent"] = memory_data.get("percent")
    return memory_usage


def get_environ(pid):
    """Gets env vars for a specific process based on pid

    Args:
        pid (int): process pid

    Raises:
        j.exceptions.NotFound: if the process is no longer exists.
        j.exceptions.Permission: if the process is not accessible by the user.

    Returns:
        dict: dict of env variables
    """
    try:
        proc = get_process_object(pid, die=True)
        return proc.environ()
    except psutil.NoSuchProcess:
        raise j.exceptions.NotFound("Process is no longer exists")
    except psutil.AccessDenied:
        raise j.exceptions.Permission("Permission denied")


def kill_proc_tree(
    parent, sig=signal.SIGTERM, include_parent=True, include_grand_children=True, timeout=5, sure_kill=False
):
    """Kill a process and its children (including grandchildren) with signal `sig`

    Args:
        proc (int or psutil.Process): Target process ID (PID) or psutil.Process object.
        sig (signal, optional): See signal module constants. Defaults to signal.SIGTERM.
        include_parent (): Whether to kill the process itself. Defaults to True.
        include_grand_children (): whether to kill recursively all grandchildren. Defaults to True.
        timeout (int, optional): How long to wait for a process to terminate (seconds) before raise exception\
            or, if sure_kill=True, send a SIGKILL. Defaults to 5.
        sure_kill (bool, optional): Whether to fallback to SIGKILL if the timeout exceeded for the terminate operation or not. Defaults to False.

    Returns:
        list of psutil.Process: represents the objects of the processes remaning alive if any.

    Raises:
        AssertionError: in case the given `parent` is the current process
    """
    if isinstance(parent, int):
        parent = get_process_object(parent)
        if parent is None:
            return  # already dead

    # should be checked on any killing function
    # here we first need to make sure taht `include_parent` is True
    # and/or better check inside the below for loop
    assert parent.pid != os.getpid(), "won't kill myself"

    processes = parent.children(recursive=include_grand_children)[::-1]
    failed = []
    if include_parent:
        processes.append(parent)

    for p in processes:
        try:
            kill(p, sig=sig, timeout=timeout, sure_kill=sure_kill)
        except (j.exceptions.Runtime, j.exceptions.Permission):
            failed.append(p)

    # making sure
    if failed:
        gone, failed = psutil.wait_procs(failed, timeout=0)
    return failed


def in_docker():
    """will check if we are in a docker.

    Returns:
        bool: True if in docker. False otherwise.
    """
    rc, out, _ = j.sals.process.execute("cat /proc/1/cgroup", die=False, showout=False)
    return rc == 0 and "/docker/" in out


def in_host():
    """Will check if we are in a host.

    Returns:
        bool: True if in host. False otherwise.
    """
    return not in_docker()
