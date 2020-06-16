"""
Executor remote allows executing commands within specific env on the local machine. using the executor framework you can retrieve the stdout, stderr, and the return code as well.

```
JS-NG> with j.core.executors.RemoteExecutor(host="localhost", connect_kwargs={"key_filename":
                                                                              "/home/xmonader/.ssh/id_rsa",}) as c:
            c.run("hostname")
xmonader-ThinkPad-E580
JS-NG>
```
"""


import fabric

from .command_builder import cmd_from_args


@cmd_from_args
def execute(cmd, command_ctx, connection_ctx):
    """
    execute a command on a remote context

    Args:
        cmd (str or list): command as a string or an argument list, e.g. `"ls -la"` or `["ls", "la"]`
        command_ctx (dict): command runner context (the same as local `execute`)
        connection_ctx (dict): context passed to fabric e.g. fabric.Connection(host, user=None, port=None, config=None, gateway=None, forward_agent=None, connect_timeout=None, connect_kwargs=None, inline_ssh_env=None)

    Returns:
        tuple: return code, stdout, stderr
    """
    with fabric.Connection(**connection_ctx) as c:
        res = c.run(cmd, **command_ctx)
        return res.return_code, res.stdout, res.stderr


class RemoteExecutor:
    def __init__(self, **connection_ctx):
        self._connection_ctx = connection_ctx

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        pass

    @property
    def connection(self):
        return fabric.Connection(**self._connection_ctx)

    @property
    def sftp(self):
        return self.connection.sftp()

    def run(self, cmd, **command_ctx):
        """
        execute a command

        Args:
            cmd (str or list): "ls -la" or ["ls", "-la"]

        Returns:
            tuple: return code, stdout, stderr
        """
        return execute(cmd, command_ctx, self._connection_ctx)
