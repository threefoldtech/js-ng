from jumpscale.core.base import StoredFactory

from .sshkey import SSHKeyClient


export_module_as = StoredFactory(SSHKeyClient)
