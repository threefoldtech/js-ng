from jumpscale.core.base import StoredFactory

from .sshclient import SSHClient


export_module_as = StoredFactory(SSHClient)
