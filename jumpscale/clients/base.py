import os
from secretconf import read_config, save_config

from jumpscale.core.base import Base, Factory
from jumpscale.core.config import Environment


class InvalidPrivateKey(Exception):
    pass


class ConfigStore:
    """a config storage interface"""

    def __init__(self, type_):
        self.type = type_

    def get(self, instance_name):
        raise NotImplementedError

    def get_all(self):
        raise NotImplementedError

    def save(self, instance_name, data):
        raise NotImplementedError


class FileSystemStore(ConfigStore):
    def __init__(self, type_):
        self.config_env = Environment()
        self.priv_key = self.config_env.get_private_key()

        if not self.priv_key:
            raise InvalidPrivateKey

        self.root = self.config_env.get_secure_config_path()
        self.location = os.path.join(*type_.__module__.split("."))
        self.type_root = os.path.join(self.root, self.location)

        super(FileSystemStore, self).__init__(type_)

    def get_path(self, instance_name):
        return os.path.join(self.type_root, instance_name)

    def get(self, instance_name):
        path = self.get_path(instance_name)
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            os.mknod(path)
        return read_config(instance_name, path, self.priv_key)[instance_name]

    def get_all_names(self):
        if not os.path.exists(self.type_root):
            return []
        return os.listdir(self.type_root)

    def get_all(self):
        return {name: self.get(name) for name in self.get_all_names()}

    def save(self, instance_name, data):
        path = self.get_path(instance_name)
        return save_config(instance_name, data, path, self.priv_key)

    def delete(self, instance_name):
        path = self.get_path(instance_name)
        if os.path.exists:
            os.remove(path)


class SecureConfigSource:
    def __init__(self, obj):
        self.owner = obj
        self.store = FileSystemStore(type(obj))
        self._instance_name = obj.instance_name

    @property
    def instance_name(self):
        return self._instance_name

    @property
    def data(self):
        try:
            return self.store.get(self.instance_name)
        except Exception:
            return {}

    @data.setter
    def data(self, data):
        return self.store.save(self.instance_name, data)


class SecureClient(Base):
    def __init__(self, client):
        self.config = SecureConfigSource(client)


class ClientFactory(Factory):
    def __init__(self, type_):
        self.store = FileSystemStore(type_)
        super(ClientFactory, self).__init__(type_)
        self.load()

    def new(self, name, *args, **kwargs):
        if not "instance_name" in kwargs:
            kwargs["instance_name"] = name

        return super(ClientFactory, self).new(name, *args, **kwargs)

    def load(self):
        for name in self.store.get_all_names():
            self.new(name)

    def delete(self, name):
        self.store.delete(name)
        super(ClientFactory, self).delete(name)

