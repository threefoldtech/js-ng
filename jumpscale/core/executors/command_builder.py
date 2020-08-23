from functools import wraps
from subprocess import list2cmdline


def format_cmd(cmd):
    ## code around it to run in tmux.
    pass


def cmd_from_args(func):
    """
    a decorator to allow passing cmd as a list, with auto-escaping using `subprocess.list2cmdline`

    cmd must be the first positional arguments

    Args:
        func (function): the function to decorate

    Returns:
        function: a new function
    """

    @wraps(func)
    def inner(cmd, *args, **kwargs):
        if isinstance(cmd, list):
            cmd = list2cmdline(cmd)

        return func(cmd, *args, **kwargs)

    return inner
