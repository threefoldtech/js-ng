from jumpscale.core.base import StoredFactory

from .sshkey import SSHKeyClient


module_export_as = StoredFactory(SSHKeyClient)
