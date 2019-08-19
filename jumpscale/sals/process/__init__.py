import os
import os.path
import re
import time
import sys

# import select
# import threading
# import queue
import random

try:
    import psutil
except:
    pass
import subprocess
import signal
from subprocess import Popen
import select
from jumpscale.god import j

# for execute
from fcntl import fcntl, F_GETFL, F_SETFL
from os import O_NONBLOCK, read


def executeWithoutPipe(command, die=True, printCommandToStdout=False):
    """

    Execute command without opening pipes, returns only the exitcode
    This is platform independent
    @param command: command to execute
    @param die: boolean to die if got non zero exitcode
    @param printCommandToStdout: boolean to show/hide output to stdout
    @param showout: Deprecated. Use 'printCommandToStdout' instead.
    @rtype: integer represents the exitcode
    if exitcode is not zero then the executed command returned with errors
    """

    exitcode = os.system(command)

    if exitcode != 0 and die:
        
        raise j.exceptions.RuntimeError("Error during execution!\nCommand: %s\nExitcode: %s" % (command, exitcode))

    return exitcode

def execute(
    cmd,
    showout=True,
    useShell=True,
    cwd=None,
    timeout=600,
    die=True,
    async_=False,
    env=None,
    interactive=False,
    replace=False,
    args={},
):
    """

    :param command:
    :param showout: show the output while executing
    :param useShell: use a shell when executing, std True
    :param cwd: directory to go to when executing
    :param timeout: timout in sec, std 10 min
    :param die: die when not ok
    :param async_: return the pipe, don't wait
    :param env: is arguments which will be replaced om the command core.text_replace(... feature)
    :return: (rc,out,err)
    """
    return j.core.executors.run_local(
        cmd=cmd,
        timeout=timeout,
        env=env,
    )


def executeInteractive(command, die=True):
    exitcode = os.system(command)
    if exitcode != 0 and die:
        raise j.exceptions.Base("Could not execute %s" % command)
    return exitcode

def isPidAlive(pid):
    """Checks whether this pid is alive.
        For unix, a signal is sent to check that the process is alive.
        For windows, the process information is retrieved and it is double checked that the process is python.exe
        or pythonw.exe
    """
    
    if j.data.platform.is_linux():
        # Unix strategy: send signal SIGCONT to process pid
        # Achilles heal: another process which happens to have the same pid could be running
        # and incorrectly considered as this process
        import signal

        try:
            os.kill(pid, 0)
        except OSError:
            return False

        return True



def checkInstalled(cmdname):
    """
    @param cmdname is cmd to check e.g. curl
    """
    return j.core.tools.cmd_installed(cmdname)

def kill(pid, sig=None):
    """
    Kill a process with a signal
    @param pid: pid of the process to kill
    @param sig: signal. If no signal is specified signal.SIGKILL is used
    """
    pid = int(pid)
    
    if j.data.platform.is_linux():
        try:
            if sig is None:
                sig = signal.SIGKILL

            os.kill(pid, sig)

        except OSError as e:
            raise j.exceptions.RuntimeError("Could not kill process with id %s.\n%s" % (pid, e))


def psfind(name):
    rc, out, err = execute("ps ax | grep %s" % name, showout=False)
    for line in out.split("\n"):
        if line.strip() == "":
            continue
        if "grep" in line:
            continue
        return True
    return False

def killall(name):
    rc, out, err = execute("ps ax | grep %s" % name, showout=False)
    for line in out.split("\n"):
        # print("L:%s" % line)
        if line.strip() == "":
            continue
        if "grep" in line:
            continue
        line = line.strip()
        pid = line.split(" ")[0]
        
        kill(pid)
    if psfind(name):
        raise j.exceptions.Base("Could not kill:%s, is still, there check if its not autorestarting." % name)

def getPidsByFilterSortable(filterstr, sortkey=None):
    """
    Get pids of process by a filter string and optionally sort by sortkey

    @param filterstr string: filter string.
    @param sortkey   string: sort key for ps command
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


    """
    if sortkey is not None:
        cmd = "ps aux --sort={sortkey} | grep '{filterstr}'".format(filterstr=filterstr, sortkey=sortkey)
    else:
        cmd = "ps ax | grep '{filterstr}'".format(filterstr=filterstr)
    rcode, out, err = execute(cmd)
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

def process_pids_get_by_filter(filterstr, excludes=None):
    excludes = excludes or []
    cmd = "ps ax | grep '%s'" % filterstr
    rcode, out, err = j.core.executors.run_local(cmd)
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

def getPidsByFilter(filterstr="", regex_list=None, excludes=None):
    regex_list = regex_list or []
    excludes = excludes or []
    if not regex_list:
        return process_pids_get_by_filter(filterstr, excludes=excludes)
    elif filterstr == "":
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
                    if name.strip() != "":
                        if j.data.regex.match(r, name):
                            res.append(process.pid)
        return res
    else:
        raise j.exceptions.Base("filterstr or regexes")

def checkstart(cmd, filterstr, nrtimes=1, retry=1):
    """
    @param cmd is which command to execute to start e.g. a daemon
    @param filterstr is what to check on if its running
    @param nrtimes is how many processes need to run
    """

    found = getPidsByFilter(filterstr)
    for i in range(retry):
        if len(found) == nrtimes:
            return
        # print "START:%s"%cmd
        execute(cmd)
        time.sleep(1)
        found = getPidsByFilter(filterstr)
    if len(found) != nrtimes:
        raise j.exceptions.RuntimeError(
            "could not start %s, found %s nr of instances. Needed %s." % (cmd, len(found), nrtimes)
        )

def checkstop(cmd, filterstr, retry=1, nrinstances=0):
    """
    @param cmd is which command to execute to start e.g. a daemon
    @param filterstr is what to check on if its running
    @param nrtimes is how many processes need to run
    """

    found = getPidsByFilter(filterstr)
    for i in range(retry):
        if len(found) == nrinstances:
            return
        # print "START:%s"%cmd
        execute(cmd, die=False)
        time.sleep(1)
        found = getPidsByFilter(filterstr)
        for item in found:
            kill(int(item), 9)
        found = getPidsByFilter(filterstr)

    if len(found) != 0:
        raise j.exceptions.RuntimeError("could not stop %s, found %s nr of instances." % (cmd, len(found)))

def getProcessPid(process, match_predicate=None):
    """Get process ID(s) for a given process
    
    :param process: process to look for
    :type process: str
    :param match_predicate: function that does matching between 
        found processes and the targested process, the function should accept 
        two arguments and return a boolean, defaults to None
    :type match_predicate: callable, optional
    :raises j.exceptions.RuntimeError: If process is None
    :raises NotImplementedError: If called on a non-unix system
    :return: list of matching process IDs
    :rtype: list
    """
    # default match predicate
    # why aren't we using psutil ??
    def default_predicate(given, target):
        return given.find(target.strip()) != -1

    if match_predicate is None:
        match_predicate = default_predicate

    if process is None:
        raise j.exceptions.RuntimeError("process cannot be None")
    if j.data.platform.is_linux():

        # Need to set $COLUMNS such that we can grep full commandline
        # Note: apparently this does not work on solaris
        command = "bash -c 'env COLUMNS=300 ps -ef'"
        (exitcode, output, err) = execute(command, die=False, showout=False)
        pids = list()
        co = re.compile(
            "\s*(?P<uid>[a-z]+)\s+(?P<pid>[0-9]+)\s+(?P<ppid>[0-9]+)\s+(?P<cpu>[0-9]+)\s+(?P<stime>\S+)\s+(?P<tty>\S+)\s+(?P<time>\S+)\s+(?P<cmd>.+)"
        )
        for line in output.splitlines():
            match = co.search(line)
            if not match:
                continue
            gd = match.groupdict()
            # print "%s"%line
            # print gd["cmd"]
            # print process
            if isinstance(process, int) and gd["pid"] == process:
                pids.append(gd["pid"])
            elif match_predicate(gd["cmd"], process):
                pids.append(gd["pid"])
        pids = [int(item) for item in pids]
        return pids
    else:
        raise j.exceptions.NotImplemented("getProcessPid is only implemented for unix")

def getMyProcessObject():
    return getProcessObject(os.getpid())

def getProcessObject(pid, die=True):

    for process in psutil.process_iter():
        if process.pid == pid:
            return process
    if die:
        raise j.exceptions.NotFound("Could not find process with pid:%s" % pid)

def getProcessPidsFromUser(user):

    result = []
    for process in psutil.process_iter():
        if process.username == user:
            result.append(process.pid)
    return result

def killUserProcesses(user):
    for pid in getProcessPidsFromUser(user):
        kill(pid)

def getSimularProcesses():

    myprocess = getMyProcessObject()
    result = []
    for item in psutil.process_iter():
        try:
            if item.cmdline == myprocess.cmdline:
                result.append(item)
        except psutil.NoSuchProcess:
            pass
    return result

def checkProcessRunning(process, min=1):
    """
    Check if a certain process is running on the system.
    you can specify minimal running processes needed.
    @param process: String with the name of the process we
        are trying to check
    @param min: (int) minimal threads that should run.
    @return True if ok
    """
    
    if j.data.platform.is_linux():
        pids = getProcessPid(process)
        if len(pids) >= min:
            return True
        return False

def checkProcessForPid(pid, process):
    """
    Check whether a given pid actually does belong to a given process name.
    @param pid: (int) the pid to check
    @param process: (str) the process that should have the pid
    @return status: (int) 0 when ok, 1 when not ok.
    """
    
    if j.data.platform.is_linux():
        command = "ps -p %i" % pid
        (exitcode, output, err) = execute(command, die=False, showout=False)
        i = 0
        for line in output.splitlines():
            match = re.match(".{23}.*(\s|\/)%s(\s|$).*" % process, line)
            if match:
                i = i + 1
        if i >= 1:
            return 0
        return 1


def setEnvironmentVariable(varnames, varvalues):
    """Set the value of the environment variables C{varnames}. Existing variable are overwritten

    @param varnames: A list of the names of all the environment variables to set
    @type varnames: list<string>
    @param varvalues: A list of all values for the environment variables
    @type varvalues: list<string>
    """
    try:
        for i in range(len(varnames)):
            os.environ[varnames[i]] = str(varvalues[i]).strip()
    except Exception as e:
        raise j.exceptions.RuntimeError(e)

def getPidsByPort(port):
    """
    Returns pid of the process that is listening on the given port
    """
    name = getProcessByPort(port)
    if name is None:
        return []
    # print "found name:'%s'"%name
    pids = getProcessPid(name)
    # print pids
    return pids

def killProcessByName(name, sig=None, match_predicate=None):
    """Kill all processes for a given command
    
    :param name: Name of the command that started the process(s)
    :type name: str
    :param sig: os signal to send to the process(s), defaults to None
    :type sig: int, optional
    :param match_predicate: function that does matching between 
        found processes and the targested process, the function should accept 
        two arguments and return a boolean, defaults to None
    :type match_predicate: callable, optional
    """

    pids = getProcessPid(name, match_predicate=match_predicate)
    for pid in pids:
        kill(pid, sig)

def killProcessByPort(port):
    for pid in getPidsByPort(port):
        kill(pid)

def getProcessByPort(port):
    """
    Returns the full name of the process that is listening on the given port

    @param port: the port for which to find the command
    @type port: int
    @return: full process name
    @rtype: string
    """
    if port == 0:
        return None


        for process in psutil.process_iter():
            try:
                cc = [x for x in process.connections() if x.status == psutil.CONN_LISTEN]
            except Exception as e:
                if str(e).find("psutil.AccessDenied") == -1:
                    raise j.exceptions.RuntimeError(str(e))
                continue
            if cc != []:
                for conn in cc:
                    portfound = conn.laddr[1]
                    if port == portfound:
                        return process
        return None


def getDefunctProcesses():
    rc, out, err = execute("ps ax")
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

def getEnviron(pid):
    environ = j.sal.fs.readFile("/proc/%s/environ" % pid)
    env = dict()
    for line in environ.split("\0"):
        if "=" in line:
            key, value = line.split("=", 1)
            env[key] = value
    return env
