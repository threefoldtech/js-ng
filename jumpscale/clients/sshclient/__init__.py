from jumpscale.core.base import StoredFactory

from .sshclient import SSHClient


module_export_as = StoredFactory(SSHClient)
