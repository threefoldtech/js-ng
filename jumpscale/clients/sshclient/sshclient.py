"""

SSHClient modules helps connecting and executing commands to a remote machine.


## Create SSH Key
```python
JS-NG> xmonader = j.clients.sshkey.new("xmonader")
JS-NG> xmonader.private_key_path = "/home/xmonader/.ssh/id_rsa"
JS-NG>

```

## Creating sshclient using that key and executing commands

```
JS-NG> sshkey = j.clients.sshkey.get("xmonader")
JS-NG> localclient = j.clients.sshclient.get("xmonader")
JS-NG> localclient.host = "IP of the machine to access"
JS-NG> localclient.sshclient.run("hostname")
asgard
(0, 'asgard\n', '')

```
"""

from jumpscale.clients.base import Client
from jumpscale.core.base import fields
from jumpscale.loader import j


class SSHClient(Client):
    """
    SSHClient has the following properties:
    sshkey (str): sshkey to use within that client
    host (str): host ip
    user (str): user to connect as default: True
    port (int): the port to use
    forward_agent (bool):  forward agent or not (default True)
    connect_timeout (int): timeout (default 10 seconds)

    """

    sshkey = fields.String(required=True)

    host = fields.String(default="127.0.0.1", required=True)
    user = fields.String(default="root", required=True)
    port = fields.Integer(default=22, required=True)
    forward_agent = fields.Boolean(default=True)
    connect_timeout = fields.Integer(default=10)
    connection_kwargs = fields.Typed(dict, default={})

    # gateway = ?  FIXME: should help with proxyjumps. http://docs.fabfile.org/en/2.4/concepts/networking.html#ssh-gateways

    inline_ssh_env = fields.Boolean(
        default=True
    )  # whether to send environment variables “inline” as prefixes in front of command strings (export VARNAME=value && mycommand here), instead of trying to submit them through the SSH protocol itself (which is the default behavior). This is necessary if the remote server has a restricted AcceptEnv setting (which is the common default).

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__client = None

    @property
    def _sshkey(self):
        """ Get sshkey client that you have loaded
        e.g
            JS-NG> localconnection = j.clients.sshclient.new("localconnection")
            JS-NG> localconnection.sshkey = "xmonader"
            JS-NG> localconnection._sshkey()  -> SHKeyClient(_Base__instance_name='xmonader', _Base__parent=None, ...
        Returns:
            Obj: It returns object of SSHkeyClient
        """
        return j.clients.sshkey.get(self.sshkey)

    @property
    def sshclient(self):
        self.validate()
        if not self.__client:
            self.connection_kwargs["key_filename"] = self._sshkey.private_key_path
            connection_kwargs = dict(
                host=self.host,
                user=self.user,
                port=self.port,
                forward_agent=self.forward_agent,
                connect_timeout=self.connect_timeout,
                connect_kwargs=self.connection_kwargs,
            )
            if self._sshkey.passphrase:
                connection_kwargs["connect_kwargs"]["passphrase"] = self._sshkey.passphrase

            self.__client = j.core.executors.RemoteExecutor(**connection_kwargs)

        return self.__client

    def reset_connection(self):
        """ Reset the connection
        e.g
            localconnection = j.clients.sshclient.new("localconnection")
            localconnection.reset_connection()

        """
        self.__client = None
