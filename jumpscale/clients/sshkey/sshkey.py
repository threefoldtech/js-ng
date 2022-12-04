"""
This module used to manage your ssh keys, get the public key, get the private key, generate key, write key to the file system,
delete key from the file system, load key from the file system.

# Using sshkey

```
ssh_cl = j.clients.sshkey.get("ssh_test")
```

### Load ssh key from file
```
ssh_cl.load_from_file_system()
```
### Generate ssh keys
```
ssh_cl.generate_keys()
```
### Get public key path
```
 ssh_cl.public_key_path  -> "/root/.config/jumpscale/sshkeys/tU59lc6P.pub"
```
### Writing ssh keys to files system
```
ssh_cl.write_to_filesystem()
```
"""
from jumpscale.clients.base import Client
from jumpscale.core.base import fields
from jumpscale.loader import j


class SSHKeyClient(Client):
    public_key = fields.String()
    private_key = fields.Secret()
    private_key_path = fields.Secret()
    passphrase = fields.Secret(default="")
    duration = fields.Integer()
    allow_agent = fields.Boolean()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.private_key_path and j.sals.fs.exists(self.private_key_path):
            self.load_from_file_system()

    def load_from_file_system(self):
        """ Load public key and private key from files using private key path and public key path
        e.g
            ssh_cl = j.clients.sshkey.get("ssh_test")
            ssh_cl.load_from_file_system()
        """
        self.public_key = j.sals.fs.read_file(self.public_key_path)
        self.private_key = j.sals.fs.read_file(self.private_key_path)

    def generate_keys(self):
        """Generate a new ssh key
        e.g
            ssh_cl = j.clients.sshkey.get("ssh_test")
            ssh_cl.generate_keys()
        """
        if not self.private_key_path:
            # TODO: make sure the new sshkey name doesn't exist.
            sshkeys_dir = j.sals.fs.join_paths(j.core.config.config_root, "sshkeys")
            j.sals.fs.mkdirs(sshkeys_dir)
            self.private_key_path = j.sals.fs.join_paths(sshkeys_dir, j.data.idgenerator.chars(8))
        if self.passphrase and len(self.passphrase) < 5:
            raise ValueError("invalid passphrase length: should be at least 5 chars.")
        cmd = 'ssh-keygen -f {} -N "{}"'.format(self.private_key_path, self.passphrase)
        rc, out, err = j.core.executors.run_local(cmd)
        if rc == 0:
            self.public_key = j.sals.fs.read_file(self.public_key_path)
            self.private_key = j.sals.fs.read_file(self.private_key_path)
        else:
            raise RuntimeError("couldn't create sshkey")

    @property
    def public_key_path(self):
        """ Get the public key path
        e.g
            ssh_cl = j.clients.sshkey.get("ssh_test")
            ssh_cl.public_key_path  -> "/root/.config/jumpscale/sshkeys/tU59lc6P.pub"
        Returns
            str: the path for public key

        """
        return "{}.pub".format(self.private_key_path)

    def write_to_filesystem(self):
        """ Write public key and private key to files using private key path and public key path.
        e.g
            ssh_cl = j.clients.sshkey.get("ssh_test")
            ssh_cl.write_to_filesystem()
        """
        if not self.private_key:
            raise RuntimeError("no private key to write")

        if not self.public_key:
            raise RuntimeError("no public key to write")

        j.sals.fs.write_file(self.private_key_path, self.private_key)
        j.sals.fs.write_file(self.public_key_path, self.public_key)

    def delete_from_filesystem(self):
        pass
