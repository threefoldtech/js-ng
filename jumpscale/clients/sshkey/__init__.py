from jumpscale.core.base import StoredFactory

from .sshkey import SSHKeyClient


factory = StoredFactory(SSHKeyClient)
