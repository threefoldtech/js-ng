from jumpscale.core.base import StoredFactory

from .sshclient import SSHClient


factory = StoredFactory(SSHClient)
