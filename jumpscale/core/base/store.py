"""
store defines the interface for the backend storage, let it be filesystem or redis.
this module also defines the abstractions needed for Encryption modes and different types of stores.


"""


import os
import shutil

import redis

from abc import ABC, abstractmethod
from enum import Enum

from jumpscale.data.nacl import NACL
from jumpscale.data.serializers import base64, json
from jumpscale.core.config import Environment
from jumpscale.sals.fs import read_file_binary, write_file_binary, rmtree


class InvalidPrivateKey(Exception):
    pass


class Location:
    """
    dot-separated auto-location for any type

    for example, if we have a class in jumpscale/clients/redis/<type>
    location name will be jumpscale.clients.redis.<type>
    """

    def __init__(self, *name_list):
        self.name_list = list(name_list)

    @property
    def name(self):
        return ".".join(self.name_list)

    @property
    def path(self):
        return os.path.join(*self.name.split("."))

    @classmethod
    def from_type(cls, type_):
        return cls(type_.__module__, type_.__name__)

    def __str__(self):
        args = "', '".join(self.name_list)
        cls_name = self.__class__.__name__
        return f"{cls_name}('{args}')"

    __repr__ = __str__


class EncryptionMode(Enum):
    """Encryption mode used to configure storing mode for full blown stores.
    """

    Encrypt = 0
    Decrypt = 1


class EncryptionMixin:
    def encrypt(self, data):
        """encrypt data

        Args:
            data (str): input string

        Returns:
            bytes: encrypted data as byte string
        """
        if not isinstance(data, bytes):
            data = data.encode()
        return self.nacl.encrypt(data, self.public_key)

    def decrypt(self, data):
        """decrypt data

        Args:
            data (bytes): encrypted byte string

        Returns:
            str: decrypted data
        """
        return self.nacl.decrypt(data, self.public_key).decode()


class ConfigStore(ABC):
    """the interface every config store should implement which is read, write, list_all, delete."""

    @abstractmethod
    def read(self, instance_name):
        pass

    @abstractmethod
    def write(self, instance_name, data):
        pass

    @abstractmethod
    def list_all(self):
        pass

    @abstractmethod
    def delete(self, instance_name):
        pass


class EncryptedConfigStore(ConfigStore, EncryptionMixin):
    """secure config storage base"""

    def __init__(self, location):
        self.location = location
        self.config_env = Environment()
        self.priv_key = base64.decode(self.config_env.get_private_key())
        self.nacl = NACL(private_key=self.priv_key)
        self.public_key = self.nacl.public_key.encode()

        if not self.priv_key:
            raise InvalidPrivateKey

    def _encrypt_value(self, value):
        return base64.encode(self.encrypt(value)).decode("ascii")

    def _decrypt_value(self, value):
        return self.decrypt(base64.decode(value))

    def _process_config(self, config, mode):
        """return the config encrypted or decrypted

        Args:
            config (dict): config dict (can be nested)
            mode (EncryptionMode)
        """
        new_config = {}
        for name, value in config.items():
            if name.startswith("__"):
                if mode == EncryptionMode.Decrypt:
                    new_config[name.lstrip("__")] = self._decrypt_value(value)
                else:
                    # preserve __ to know it's an encrypted value
                    new_config[name] = self._encrypt_value(value)
            elif isinstance(value, dict):
                new_config[name] = self._process_config(value, mode)
            else:
                new_config[name] = value
        return new_config

    def get(self, instance_name):
        """get instance config

        Args:
            instance_name (str): instance name

        Returns:
            dict: instance config as dict (key, values)
        """
        config = json.loads(self.read(instance_name))
        return self._process_config(config, EncryptionMode.Decrypt)

    def get_all(self):
        return {name: self.get(name) for name in self.list_all()}

    def save(self, instance_name, config):
        """save instance config

        Args:
            instance_name (str): name of instnace
            config (dict): config data, any key that starts with `__` will be encrypted

        Returns:
            bool: written or not
        """
        new_config = self._process_config(config, EncryptionMode.Encrypt)
        return self.write(instance_name, json.dumps(new_config))


class FileSystemStore(EncryptedConfigStore):
    """Filesystem store is an EncryptedConfigStore
    It saves the config relative to `config_env.get_store_config("filesystem")`

    """

    def __init__(self, location):
        super(FileSystemStore, self).__init__(location)
        self.root = self.config_env.get_store_config("filesystem")["path"]

    @property
    def config_root(self):
        return os.path.join(self.root, self.location.path)

    def get_instance_root(self, instance_name):
        return os.path.join(self.config_root, instance_name)

    def get_path(self, instance_name):
        return os.path.join(self.get_instance_root(instance_name), "data")

    def make_path(self, path):
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            os.mknod(path)

    def read(self, instance_name):
        path = self.get_path(instance_name)
        return read_file_binary(path)

    def list_all(self):
        if not os.path.exists(self.config_root):
            return []
        return os.listdir(self.config_root)

    def write(self, instance_name, data):
        path = self.get_path(instance_name)
        self.make_path(path)
        return write_file_binary(path, data.encode())

    def delete(self, instance_name):
        path = self.get_instance_root(instance_name)
        if os.path.exists(path):
            rmtree(path)


class RedisStore(EncryptedConfigStore):
    """RedisStore store is an EncryptedConfigStore
    It saves the data in redis and configuration for redis comes from `config_env.get_store_config("redis")`
    """

    def __init__(self, location):
        super().__init__(location)
        redis_config = self.config_env.get_store_config("redis")
        self.redis_client = redis.Redis(redis_config["hostname"], redis_config["port"])

    def get_key(self, instance_name):
        return ".".join([self.location.name, instance_name])

    def read(self, instance_name):
        return self.redis_client.get(self.get_key(instance_name))

    def get_location_keys(self):
        return self.redis_client.keys(f"{self.location.name}.*")

    def get_instance_keys(self, instance_name):
        return self.redis_client.keys(f"{self.location.name}.{instance_name}*")

    def list_all(self):
        names = []

        keys = self.get_location_keys()
        for key in keys:
            name = key.decode().replace(self.location.name, "").lstrip(".")
            if "." not in name:
                names.append(name)
        return names

    def write(self, instance_name, data):
        return self.redis_client.set(self.get_key(instance_name), data)

    def delete(self, instance_name):
        return self.redis_client.delete(*self.get_instance_keys(instance_name))
