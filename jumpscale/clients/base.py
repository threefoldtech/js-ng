import os
from functools import partial

from jumpscale.core.base import Base, Factory
from jumpscale.core.config import Environment
from jumpscale.data.nacl import NACL
from jumpscale.data.serializers import base64, json
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
    def __init__(self, type_):
        super(FileSystemStore, self).__init__(type_)

        self.root = self.config_env.get_secure_config_path()
        self.location = os.path.join(*type_.__module__.split("."), type_.__name__)
        self.config_root = os.path.join(self.root, self.location)

    def get_path(self, instance_name):
        return os.path.join(self.config_root, instance_name)

    def make_path(self, path):
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            os.mknod(path)

    def read(self, instance_name):
        path = self.get_path(instance_name)
        return readFile(path, binary=True)

    def list_all(self):
        if not os.path.exists(self.config_root):
            return []
        return os.listdir(self.config_root)

    def write(self, instance_name, data):
        path = self.get_path(instance_name)
        self.make_path(path)
        return writeFile(path, data)

    def delete(self, instance_name):
        path = self.get_path(instance_name)
        if os.path.exists:
            os.remove(path)


class StoredFactory(Factory):
    def __init__(self, type_):
        self.store = FileSystemStore(type_)
        super(StoredFactory, self).__init__(type_)
        self.load()

    def save_instance(self, name):
        data = self.get(name).get_data()
        self.store.save(name, json.dumps(data))

    def instance_updated(self, name, prop_name, new_value):
        self.save_instance(name)

    def instance_sub_factory_updated(self, name, new_count):
        self.save_instance(name)

    def new(self, name, *args, **kwargs):
        instance = super().new(name, *args, **kwargs)
        instance.data_updated = partial(self.instance_updated, name)

        for factory in instance.get_factories().values():
            factory.updated = partial(self.instance_sub_factory_updated, name)

        return instance

    def load(self):
        for name in self.store.list_all():
            instance = self.new(name)
            instance.set_data(json.loads(self.store.get(name)))

    def delete(self, name):
        self.store.delete(name)
        super(StoredFactory, self).delete(name)


class Client(Base):
    pass

