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
import random
import re
import select
import signal
import subprocess
import sys
import time
from collections import defaultdict
from subprocess import Popen

import psutil
import socket
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
    """
    execute a command.

    accepts command as a list too, with auto-escaping.

    Arguments:
        cmd (str or list): command to be executed, e.g. `"ls -la"` or `["ls", "-la"]

    Keyword Arguments:
        showout (bool): show stdout of the command (default: False)
        cwd (str): specify a working directory for the command (default: None)
        shell (str): specify a shell to execute the command (default: "/bin/bash")
        timeout (int): timeout before kill the process (default: 600)
        asynchronous (bool): execute in asynchronous mode or not (default: False)
        env (dict): add environment variables here (default: {})
        replace_env (bool): replace entire environment with env (default: False)
        die (bool): die if command failed (default: False)

    Returns:
        tuple: (rc, out, err)
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
    """Checks if pid is Running

    Arguments:
        pid (int) -- pid of the process to be checked

    Returns:
        [bool] -- True if process is running
    """
    pid = int(pid)
    return psutil.pid_exists(pid)


def is_installed(cmd):
    """[summary]
    Checks if a specific command is available on system e.g. curl
    Arguments:
        cmd {str} -- command to be checked

    Returns:
        [bool] -- True if command is installed
    """
    rc, _, _ = execute("which %s" % cmd, die=False)
    if rc:
        return False
    else:
        return True


def kill(pid, sig=signal.SIGTERM.value):
    """Kill a process with a signal

    Arguments:
        pid (int) -- pid of the process to be killed

    Keyword Arguments:
        sig {int]} -- which signal you want to kill the process with (default: {signal.SIGTERM.value})

    Raises:
        j.exceptions.RuntimeError: in case killing process failed

    Returns:
        [type] -- [description]
    """
    pid = int(pid)
    sig = int(sig)
    proc = psutil.Process(pid)
    try:
        proc.send_signal(sig)
        return True
    except Exception as e:
        raise j.exceptions.RuntimeError("Could not kill process with id %s.\n%s" % (pid, e))


def ps_find(name):
    """find process by name

    Arguments:
        name {str} -- process name

    Returns:
        [bool] -- True if process is found
    """
    for proc in psutil.process_iter():
        if proc.name() == name:
            return True
    return False


def kill_all(name, sig=signal.SIGKILL):
    """Kill all processes with a given name

    Arguments:
        name {str} -- process name

    Keyword Arguments:
        sig (int) -- signal number (default: {signal.SIGKILL})
    """
    sig = int(sig)
    for proc in psutil.process_iter():
        if proc.name() == name:
            kill(proc.pid, sig)


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


def check_start(cmd, filterstr, nrinstances=1, retry=1):
    """Run command and check if it is started based on filterstr

    Arguments:
        cmd {str} -- command to be executed
        filterstr {str} -- filter string

    Keyword Arguments:
        instances (int) -- number of needed instances (default: {1})
        retry (int) -- number of retries (default: {1})

    Raises:
        j.exceptions.RuntimeError: will be raised if we didn't reach number of required instances
    """
    found = get_filtered_pids(filterstr)
    for i in range(retry):
        if len(found) == nrinstances:
            return
        # print "START:%s"%cmd
        execute(cmd)
        time.sleep(1)
    found = get_filtered_pids(filterstr)
    if len(found) != nrinstances:
        raise j.exceptions.RuntimeError(
            "could not start %s, found %s nr of instances. Needed %s." % (cmd, len(found), nrinstances)
        )


def check_stop(cmd, filterstr, retry=1, nrinstances=0):
    """Executes a stop command and check if it is already stopped based on filterstr

    Arguments:
        cmd {str} -- command to be executed
        filterstr {str} -- filter string

    Keyword Arguments:
        retry (int) -- number of retries (default: {1})
        nrinstances (int) -- number of instances after stop (default: {0})

    Raises:
        j.exceptions.RuntimeError: if nr of instances not matched
    """

    found = get_filtered_pids(filterstr)
    for i in range(retry):
        if len(found) == nrinstances:
            return
        # print "START:%s"%cmd
        execute(cmd, die=False)
        time.sleep(1)
        found = get_filtered_pids(filterstr)
        for item in found:
            kill(int(item), 9)
        found = get_filtered_pids(filterstr)

    if len(found) != 0:
        raise j.exceptions.RuntimeError("could not stop %s, found %s nr of instances." % (cmd, len(found)))


def get_pids(process_name, match_predicate=None):
    """Get process ID(s) for a given process

    Arguments:
        process {str} -- process name

    Keyword Arguments:
        match_predicate {callable} -- function that does matching between
        found processes and the targested process, the function should accept
        two arguments and return a boolean, defaults to None (default: {None})

    Raises:
        j.exceptions.RuntimeError: [description]
        j.exceptions.NotImplemented: [description]

    Returns:
        [list(int)] -- list of pids
    """
    # default match predicate
    # why aren't we using psutil ??
    def default_predicate(target, given):
        return target.strip().lower() in given.lower()

    if match_predicate is None:
        match_predicate = default_predicate

    if process_name is None:
        raise j.exceptions.RuntimeError("process cannot be None")
    if j.data.platform.is_unix():
        pids = set()
        for process in get_processes():
            try:
                pid = process.pid
                if not isinstance(pid, int):
                    continue
                name = process.name()
                if match_predicate(process_name, name):
                    pids.add(pid)
                elif match_predicate(process_name, process.exe()):
                    pids.add(pid)
                else:
                    cmdline = process.cmdline()
                    if cmdline and cmdline[0]:
                        if match_predicate(process_name, cmdline[0]):
                            pids.add(pid)
            except (psutil.Error, FileNotFoundError):
                continue
        return list(pids)
    else:
        raise j.exceptions.NotImplemented("getProcessPid is only implemented for unix")


def get_my_process():
    """get process object of current process

    Returns:
        [psutil.Process] -- process object
    """
    return get_process_object(os.getpid())


def get_process_object(pid, die=True):
    """Get Process object of a process id

    Arguments:
        pid (int) -- pid of the process

    Keyword Arguments:
        die {bool} -- die if process not found (default: {True})

    Raises:
        psutil.NoSuchProcess: if process not found and die = True

    Returns:
        [psutil.Process] -- process object
    """
    try:
        return psutil.Process(pid)
    except psutil.NoSuchProcess as e:
        if die:
            raise e
        else:
            return None


def get_user_processes(user):
    """Get all process for a specific user

    Arguments:
        user {str} -- username

    Returns:
        [list(int)] -- list of process pids for that user
    """
    result = []
    for process in psutil.process_iter():
        if process.username() == user:
            result.append(process.pid)
    return result


def kill_user_processes(user):
    """Kill all processes for a specific user

    Arguments:
        user {str} -- username
    """
    for pid in get_user_processes(user):
        kill(pid)


def get_similar_processes():
    """Gets similar processes to current process

    Returns:
        [list(psutil.Process)] -- list of similar process
    """
    myprocess = get_my_process()
    result = []
    for item in psutil.process_iter():
        try:
            if item.cmdline() == myprocess.cmdline():
                result.append(item)
        except psutil.NoSuchProcess:
            pass
    return result


def check_running(process, min=1):
    """Checks if a process is running

    Arguments:
        process {str} -- process name to be checked

    Keyword Arguments:
        min (int) -- min number of instances required to be running (default: {1})

    Returns:
        [bool] -- true if process is running
    """
    if j.data.platform.is_linux():
        pids = get_pids(process)
        if len(pids) >= min:
            return True
        return False


def check_process_for_pid(pid, process_name):
    """Check whether a given pid actually does belong to a given process name.

    Arguments:
        pid (int) -- process pid
        process {str} -- process name

    Returns:
        [bool] -- True if process_name matched process name of the pid
    """
    pid = int(pid)
    proc = psutil.Process(pid)
    return proc.name() == process_name


def set_env_var(varnames, varvalues):
    """Set the value of the environment variables C{varnames}. Existing variable are overwritten

    Arguments:
        varnames {list(str)} --  A list of the names of all the environment variables to set
        varvalues {list(str)} -- A list of all values for the environment variables

    """
    try:
        for i in range(len(varnames)):
            os.environ[varnames[i]] = str(varvalues[i]).strip()
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


def kill_process_by_name(name, sig=signal.SIGTERM.value, match_predicate=None):
    """Kill all processes for a given command

    Arguments:
        name {str} -- Name of the command that started the process(s)

    Keyword Arguments:
        sig {bool} -- os signal to send to the process(s) (default: {signal.SIGTERM.value})
        match_predicate {callable} -- function that does matching between
            found processes and the targested process, the function should accept
            two arguments and return a boolean (default: {None})
    """

    pids = get_pids(name, match_predicate=match_predicate)
    for pid in pids:
        kill(pid, sig)


def kill_process_by_port(port):
    """Kill process by port

    Arguments:
        port (int) -- port number
    """
    port = int(port)
    pid = get_pid_by_port(port)
    if pid:
        return kill(pid)


def is_port_listening(port):
    """check if the port is being used by any process

    Args:
        port (int): port number

    Returns:
        Bool: True if port is used else False
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        result = s.connect_ex(("127.0.0.1", port))
    return result == 0


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
    pcons = [proc for proc in psutil.net_connections() if proc.laddr.port == port and proc.status == "LISTEN"]
    if pcons:
        pid = pcons[0].pid
        if not pid:
            raise j.exceptions.Runtime("No pid found maybe permission denied on the process")
        return psutil.Process(pid)


def get_defunct_processes():
    """Gets defunc processes

    Returns:
        [list(int)] -- list of processes pids
    """
    _, out, _ = execute("ps ax")
    llist = []
    for line in out.split("\n"):
        if line.strip() == "":
            continue
        if line.find("<defunct>") != -1:
            # print "defunct:%s"%line
            line = line.strip()
            pid = line.split(" ", 1)[0]
            pid = int(pid.strip())
            llist.append(pid)

    return llist


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
