"""
Local executor allows executing commands within specific env on the local machine. using the executor framework you can retrieve the stdout, stderr, and the return code as well.
```
JS-NG> j.core.executors.run_local("echo $WHOME", env={'WHOME':'abc'}, ech
     1 o=True)
echo $WHOME
abc
<Result cmd='echo $WHOME' exited=0>

JS-NG> j.core.executors.run_local("uname", echo=True)
uname
Linux
<Result cmd='uname' exited=0>

JS-NG> j.core.executors.run_local("uname", echo=False)
Linux
<Result cmd='uname' exited=0>
```


"""
import invoke

from .command_builder import cmd_from_args


@cmd_from_args
def execute(cmd, **command_ctx):
    """execute `cmd` locally

    Args:
        cmd: command (str): The shell command to execute.

    Keyword args:
        command (str): The shell command to execute.
        shell (str): Which shell binary to use. Default: /bin/bash (on Unix; COMSPEC or cmd.exe on Windows.)
        warn (bool): Whether to warn and continue, instead of raising UnexpectedExit, when the executed command exits with a nonzero status. Default: False.
            Note
            This setting has no effect on exceptions, which will still be raised, typically bundled in ThreadException objects if they were raised by the IO worker threads.

            Similarly, WatcherError exceptions raised by StreamWatcher instances will also ignore this setting, and will usually be bundled inside Failure objects (in order to preserve the execution context).

            Ditto CommandTimedOut - basically, anything that prevents a command from actually getting to “exited with an exit code” ignores this flag.

        hide (bool or NoneType): Allows the caller to disable run’s default behavior of copying the subprocess’ stdout and stderr to the controlling terminal. Specify hide='out' (or 'stdout') to hide only the stdout stream, hide='err' (or 'stderr') to hide only stderr, or hide='both' (or True) to hide both streams.
            The default value is None, meaning to print everything; False will also disable hiding.

            Note
            Stdout and stderr are always captured and stored in the Result object, regardless of hide’s value.

            Note
            hide=True will also override echo=True if both are given (either as kwargs or via config/CLI).

        pty (bool): By default, run connects directly to the invoked process and reads its stdout/stderr streams. Some programs will buffer (or even behave) differently in this situation compared to using an actual terminal or pseudoterminal (pty). To use a pty instead of the default behavior, specify pty=True.
            Warning
            Due to their nature, ptys have a single output stream, so the ability to tell stdout apart from stderr is not possible when pty=True. As such, all output will appear on out_stream (see below) and be captured into the stdout result attribute. err_stream and stderr will always be empty when pty=True.

        fallback (bool): Controls auto-fallback behavior re: problems offering a pty when pty=True. Whether this has any effect depends on the specific Runner subclass being invoked. Default: True.
        asynchronous (bool): When set to True (default False), enables asynchronous behavior, as follows:
            Connections to the controlling terminal are disabled, meaning you will not see the subprocess output and it will not respond to your keyboard input - similar to hide=True and in_stream=False (though explicitly given (out|err|in)_stream file-like objects will still be honored as normal).
            run returns immediately after starting the subprocess, and its return value becomes an instance of Promise instead of Result.
            Promise objects are primarily useful for their join method, which blocks until the subprocess exits (similar to threading APIs) and either returns a final Result or raises an exception, just as a synchronous run would.
            As with threading and similar APIs, users of asynchronous=True should make sure to join their Promise objects to prevent issues with interpreter shutdown.
            One easy way to handle such cleanup is to use the Promise as a context manager - it will automatically join at the exit of the context block.
            New in version 1.4.

        disown (bool): When set to True (default False), returns immediately like asynchronous=True, but does not perform any background work related to that subprocess (it is completely ignored). This allows subprocesses using shell backgrounding or similar techniques (e.g. trailing &, nohup) to persist beyond the lifetime of the Python process running Invoke.
            Note
            If you’re unsure whether you want this or asynchronous, you probably want asynchronous!

            Specifically, disown=True has the following behaviors:

            The return value is None instead of a Result or subclass.
            No I/O worker threads are spun up, so you will have no access to the subprocess’ stdout/stderr, your stdin will not be forwarded, (out|err|in)_stream will be ignored, and features like watchers will not function.
            No exit code is checked for, so you will not receive any errors if the subprocess fails to exit cleanly.
            pty=True may not function correctly (subprocesses may not run at all; this seems to be a potential bug in Python’s pty.fork) unless your command line includes tools such as nohup or (the shell builtin) disown.
            New in version 1.4.

        echo (bool): Controls whether run prints the command string to local stdout prior to executing it. Default: False.
            Note
            hide=True will override echo=True if both are given.

        env (dict): By default, subprocesses receive a copy of Invoke’s own environment (i.e. os.environ). Supply a dict here to update that child environment.
            For example, run('command', env={'PYTHONPATH': '/some/virtual/env/maybe'}) would modify the PYTHONPATH env var, with the rest of the child’s env looking identical to the parent.

            See also
            replace_env for changing ‘update’ to ‘replace’.

        replace_env (bool): When True, causes the subprocess to receive the dictionary given to env as its entire shell environment, instead of updating a copy of os.environ (which is the default behavior). Default: False.
        encoding (str): Override auto-detection of which encoding the subprocess is using for its stdout/stderr streams (which defaults to the return value of default_encoding).
        out_stream: A file-like stream object to which the subprocess’ standard output should be written. If None (the default), sys.stdout will be used.
        err_stream: Same as out_stream, except for standard error, and defaulting to sys.stderr.
        in_stream: A file-like stream object to used as the subprocess’ standard input. If None (the default), sys.stdin will be used.
            If False, will disable stdin mirroring entirely (though other functionality which writes to the subprocess’ stdin, such as autoresponding, will still function.) Disabling stdin mirroring can help when sys.stdin is a misbehaving non-stream object, such as under test harnesses or headless command runners.

        watchers: A list of StreamWatcher instances which will be used to scan the program’s stdout or stderr and may write into its stdin (typically str or bytes objects depending on Python version) in response to patterns or other heuristics.
            See Automatically responding to program output for details on this functionality.
            Default: [].

        echo_stdin (bool): Whether to write data from in_stream back to out_stream.
            In other words, in normal interactive usage, this parameter controls whether Invoke mirrors what you type back to your terminal.

            By default (when None), this behavior is triggered by the following:

            Not using a pty to run the subcommand (i.e. pty=False), as ptys natively echo stdin to stdout on their own;
            And when the controlling terminal of Invoke itself (as per in_stream) appears to be a valid terminal device or TTY. (Specifically, when isatty yields a True result when given in_stream.)
            Note
            This property tends to be False when piping another program’s output into an Invoke session, or when running Invoke within another program (e.g. running Invoke from itself).

            If both of those properties are true, echoing will occur; if either is false, no echoing will be performed.

            When not None, this parameter will override that auto-detection and force, or disable, echoing.

        timeout: Cause the runner to submit an interrupt to the subprocess and raise CommandTimedOut, if the command takes longer than timeout seconds to execute. Defaults to None, meaning no timeout.

    Raises:
        UnexpectedExit: if the command exited nonzero and warn was False.
        Failure: if the command didn’t even exit cleanly, e.g. if a StreamWatcher raised WatcherError.
        ThreadException: (if the background I/O threads encountered exceptions other than WatcherError).

    Returns:
        tuple: return code, stdout, stderr (from invoke.run `Result`)
    """
    ## use formatter to format command
    command_ctx = command_ctx or {}
    if "cwd" in command_ctx:
        if command_ctx["cwd"]:
            cwd = command_ctx["cwd"]
            del command_ctx["cwd"]
            c = invoke.Context()
            with c.cd(cwd):
                res = c.run(cmd, **command_ctx)
                return res.return_code, res.stdout, res.stderr
        del command_ctx["cwd"]
    res = invoke.run(cmd, **command_ctx)
    return res.return_code, res.stdout, res.stderr
