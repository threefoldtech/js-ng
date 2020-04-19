def export_module_as():
    from jumpscale.core.base import StoredFactory

    from .sshkey import SSHKeyClient

    return StoredFactory(SSHKeyClient)
