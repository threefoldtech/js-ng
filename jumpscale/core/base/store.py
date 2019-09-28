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
    """dot-separated auto-location for any type

    for example, if we have a class in jumpscale/clients/redis/<type>
    location name will be jumpscale.clients.redis.<type>

    it can have a parent of any name
    """

    def __init__(self, type_, parent_name):
        self.type = type_

        self.path_list = [self.type.__module__, self.type.__name__]
        if parent_name:
            self.path_list = [parent_name] + self.path_list

    @property
    def name(self):
        return ".".join(self.path_list)

    @property
    def path(self):
        return os.path.join(*self.name.split("."))


class EncryptionMode(Enum):
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
    """the interface every config store should implement"""

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

    # TODO: encrypt/decrypt by section (config key)

    def __init__(self, type_, parent_name=None):
        self.type = type_
        self.config_env = Environment()
        self.priv_key = base64.decode(self.config_env.get_private_key())
        self.nacl = NACL(private_key=self.priv_key)
        self.public_key = self.nacl.public_key.encode()

        if not self.priv_key:
            raise InvalidPrivateKey

        self.parent_name = parent_name

    def get_type_location(self, type_, parent_name):
        return Location(type_, parent_name)

    @property
    def location(self):
        return self.get_type_location(self.type, self.parent_name)

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
    def __init__(self, type_, parent_name=None):
        super(FileSystemStore, self).__init__(type_, parent_name)
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
    def __init__(self, type_, parent_name=None):
        super().__init__(type_, parent_name)
        redis_config = self.config_env.get_store_config("redis")
        self.redis_client = redis.Redis(redis_config["hostname"], redis_config["port"])

    def get_key(self, instance_name):
        return ".".join([self.location.name, instance_name])

    def read(self, instance_name):
        return self.redis_client.get(self.get_key(instance_name))

    def get_type_keys(self):
        return self.redis_client.keys(f"{self.location.name}.*")

    def get_instance_keys(self, instance_name):
        return self.redis_client.keys(f"{self.location.name}.{instance_name}*")

    def list_all(self):
        names = []

        keys = self.get_type_keys()
        for key in keys:
            name = key.decode().replace(self.location.name, "").lstrip(".")
            if "." not in name:
                names.append(name)
        return names

    def write(self, instance_name, data):
        return self.redis_client.set(self.get_key(instance_name), data)

    def delete(self, instance_name):
        return self.redis_client.delete(*self.get_instance_keys(instance_name))

