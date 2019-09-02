from jumpscale.clients.base import Client
from jumpscale.core.base import fields
from jumpscale.god import j

class SSHKeyClient(Client):
    name = fields.String()
    public_key = fields.String()
    private_key = fields.String() #should use secret.
    private_key_path = fields.String() # should use secret.
    passphrase = fields.String(default="") # should use secret.
    duration = fields.Integer()
    allow_agent = fields.Boolean()
    
    def __init__(self):
        super().__init__()

    def load_from_file_system(self):
        self.public_key = j.sals.fs.read_file(self.public_key_path)
        self.private_key = j.sals.fs.read_file(self.private_key_path)
        

    def generate_keys(self):
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
        return "{}.pub".format(self.private_key_path)

    def write_to_filesystem(self):
        if not self.private_key:
            raise RuntimeError("no private key to write")
        
        if not self.public_key:
            raise RuntimeError("no public key to write")
        
        j.sals.fs.write_file(self.private_key_path, self.private_key)
        j.sals.fs.write_file(self.public_key_path, self.public_key)

    def delete_from_filesystem(self):
        pass
