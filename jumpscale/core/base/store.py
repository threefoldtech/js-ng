import os

from jumpscale.data.nacl import NACL
from jumpscale.data.serializers import base64
from jumpscale.core.config import Environment
from jumpscale.sals.fs import readFile, writeFile


class InvalidPrivateKey(Exception):
    pass


class ConfigStore:
    """secure config storage base"""

    # TODO: encrypt/decrypt by section (config key)

    def __init__(self, type_):
        self.type = type_
        self.config_env = Environment()
        self.priv_key = base64.decode(self.config_env.get_private_key())
        self.nacl = NACL(private_key=self.priv_key)
        self.public_key = self.nacl.public_key.encode()

        if not self.priv_key:
            raise InvalidPrivateKey

    def read(self, instance_name):
        raise NotImplementedError

    def write(self, instance_name, data):
        raise NotImplementedError

    def list_all(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    def encrypt(self, data):
        if isinstance(data, str):
            data = data.encode()
        return self.nacl.encrypt(data, self.public_key)

    def decrypt(self, data):
        return self.nacl.decrypt(data, self.public_key)

    def get(self, instance_name):
        return self.decrypt(self.read(instance_name))

    def get_all(self):
        return {name: self.get(name) for name in self.list_all()}

    def save(self, instance_name, data):
        return self.write(instance_name, self.encrypt(data))


class FileSystemStore(ConfigStore):
    def __init__(self, type_, parent_name=None):
        super(FileSystemStore, self).__init__(type_)

        self.parent_name = parent_name
        self.root = self.config_env.get_secure_config_path()

    @property
    def config_root(self):
        return os.path.join(self.root, self.location)

    @property
    def location(self):
        location = os.path.join(*self.type.__module__.split("."), self.type.__name__)
        if self.parent_name:
            return os.path.join(location, self.parent_name)
        return location

    def get_path(self, instance_name):
        return os.path.join(self.config_root, instance_name)

    def make_path(self, path):
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            os.mknod(path)

    def read(self, instance_name):
        path = self.get_path(instance_name)
        return readFile(path, binary=True)

    def list_files(self, dir_path):
        return [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]

    def list_all(self):
        if not os.path.exists(self.config_root):
            return []
        return self.list_files(self.config_root)

    def write(self, instance_name, data):
        path = self.get_path(instance_name)
        self.make_path(path)
        return writeFile(path, data)

    def delete(self, instance_name):
        path = self.get_path(instance_name)
        if os.path.exists:
            os.remove(path)

