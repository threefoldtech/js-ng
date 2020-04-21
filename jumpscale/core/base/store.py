"""
Store defines the interface for the backend storage, let it be filesystem or redis.

This module also defines the abstractions needed for any storage backend.

Every backend should be able to organize configuration for multiple instance given a location, also
read/write the config data in raw (string) format.
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
    """
    raised when the private key configured is invalid
    """


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
        """
        get dot seprated string from current name list

        Returns:
            str: dot separated string
        """
        return ".".join(self.name_list)

    @property
    def path(self):
        """
        get a filesystem path with from `name`, where dots are replaced by `os.sep`

        Returns:
            str: path
        """
        return os.path.join(*self.name.split("."))

    @classmethod
    def from_type(cls, type_):
        """
        get a location from any type/class

        Args:
            type_ (type): any type (class)

        Returns:
            Location: a location object
        """
        return cls(type_.__module__, type_.__name__)

    def __str__(self):
        args = "', '".join(self.name_list)
        cls_name = self.__class__.__name__
        return f"{cls_name}('{args}')"

    __repr__ = __str__


class EncryptionMode(Enum):
    """
    An enum to select encryption mode based on loading or storing the data
    """

    Encrypt = 0
    Decrypt = 1


class EncryptionMixin:
    """
    A mixin that provides encrypt and decrypt methods, which can be used in any store
    """

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
    """
    the interface every config store should implement:

    - `read(instance_name)`:  reads the data of this instance name
    - `write(instance_name, data)`: writes the data of this instance
    - `list_all(instance_name)`: lists all instance names
    - `delete(instance_name)`: delete instance data
    """

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
    """the base class for any config store backend"""

    def __init__(self, location):
        self.location = location
        self.config_env = Environment()
        self.priv_key = base64.decode(self.config_env.get_private_key())
        self.nacl = NACL(private_key=self.priv_key)
        self.public_key = self.nacl.public_key.encode()

        if not self.priv_key:
            raise InvalidPrivateKey

    def _encrypt_value(self, value):
        """
        encrypt a single value

        Args:
            value (str): value

        Returns:
            str: decrypted value
        """
        return base64.encode(self.encrypt(value)).decode("ascii")

    def _decrypt_value(self, value):
        """
        decrypt a single value

        Args:
            value (str): value

        Returns:
            str: decrypted value
        """
        return self.decrypt(base64.decode(value))

    def _process_config(self, config, mode):
        """
        process current config according to encryption mode

        Args:
            config (dict): config dict (can be nested)
            mode (EncryptionMode)
        """
        new_config = {}
        for name, value in config.items():
            if name.startswith("__") and value is not None:
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
        """
        get instance config

        Args:
            instance_name (str): instance name

        Returns:
            dict: instance config as dict
        """
        config = json.loads(self.read(instance_name))
        return self._process_config(config, EncryptionMode.Decrypt)

    def save(self, instance_name, config):
        """
        save instance config

        Args:
            instance_name (str): name
            config (dict): config data, any key that starts with `__` will be encrypted

        Returns:
            bool: written or not
        """
        new_config = self._process_config(config, EncryptionMode.Encrypt)
        return self.write(instance_name, json.dumps(new_config))


class FileSystemStore(EncryptedConfigStore):
    """
    Filesystem store is an EncryptedConfigStore

    It saves the config relative to `config_env.get_store_config("filesystem")`

    To store every instance config in a different path, it uses the given `Location`.
    """

    def __init__(self, location):
        """
        create a new `FileSystemStore` that stores config at the given location under configured root.

        The root directory can be configured, see `jumpscale.core.config`

        Args:
            location (Location): where config will be stored per instance
        """
        super(FileSystemStore, self).__init__(location)
        self.root = self.config_env.get_store_config("filesystem")["path"]

    @property
    def config_root(self):
        """
        get the root directory where all configurations are written

        Returns:
            str: path
        """
        return os.path.join(self.root, self.location.path)

    def get_instance_root(self, instance_name):
        """
        get the directory where instance config is written

        Args:
            instance_name (str): name

        Returns:
            str: path
        """
        return os.path.join(self.config_root, instance_name)

    def get_path(self, instance_name):
        """
        get the path to data file where instance config is written

        Args:
            instance_name (str): name

        Returns:
            str: path
        """
        return os.path.join(self.get_instance_root(instance_name), "data")

    def make_path(self, path):
        """
        to ensure the given path, create it if it does not exist

        Args:
            path (str): path
        """
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            os.mknod(path)

    def read(self, instance_name):
        """
        read config data from the data file

        Args:
            instance_name (str): name

        Returns:
            str: data
        """
        path = self.get_path(instance_name)
        return read_file_binary(path)

    def list_all(self):
        """
        list all instance names (directories under config root)

        Returns:
            list: instance/directory names
        """
        if not os.path.exists(self.config_root):
            return []
        return os.listdir(self.config_root)

    def write(self, instance_name, data):
        """
        write config data to data file

        Args:
            instance_name (str): config
            data (str): data

        Returns:
            bool: written or not
        """
        path = self.get_path(instance_name)
        self.make_path(path)
        return write_file_binary(path, data.encode())

    def delete(self, instance_name):
        """
        delete instance config directory

        Args:
            instance_name (str):
        """
        path = self.get_instance_root(instance_name)
        if os.path.exists(path):
            rmtree(path)


class RedisStore(EncryptedConfigStore):
    """
    RedisStore store is an EncryptedConfigStore

    It saves the data in redis and configuration for redis comes from `config_env.get_store_config("redis")`
    """

    def __init__(self, location):
        """
        create a new redis store, the location given will be used to generate keys

        this keys will be combined to get/set instance config

        Args:
            location (Location)
        """
        super().__init__(location)
        redis_config = self.config_env.get_store_config("redis")
        self.redis_client = redis.Redis(redis_config["hostname"], redis_config["port"])

    def get_key(self, instance_name):
        """
        get a key for an instance

        this will return a dot-separated key derived from current location

        Args:
            instance_name (str): name

        Returns:
            str: key
        """
        return ".".join([self.location.name, instance_name])

    def read(self, instance_name):
        """
        read instance config from redis

        Args:
            instance_name (name): name

        Returns:
            str: data
        """
        return self.redis_client.get(self.get_key(instance_name))

    def _full_scan(self, pattern):
        """
        get the full result of a scan command on current redis database by this pattern

        Args:
            pattern ([type]): [description]
        """
        keys = []
        cursor, values = self.redis_client.scan(0, pattern)

        while values:
            keys += values
            if not cursor:
                break
            cursor, values = self.redis_client.scan(cursor, pattern)

        return keys

    def get_location_keys(self):
        """
        get all keys under current location (scanned)

        Returns:
            list: a list of keys
        """
        return self._full_scan(f"{self.location.name}.*")

    def get_instance_keys(self, instance_name):
        """
        get all instance related keys (scanned)

        Args:
            instance_name (str): name

        Returns:
            list: list of keys
        """
        return self._full_scan(f"{self.location.name}.{instance_name}*")

    def list_all(self):
        """
        get all names of instances (instance keys)

        Returns:
            [type]: [description]
        """
        names = []

        keys = self.get_location_keys()
        for key in keys:
            # remove location name part
            name = key.decode().replace(self.location.name, "").lstrip(".")
            if "." not in name:
                names.append(name)
        return names

    def write(self, instance_name, data):
        """
        set data with the corresponding key for this instance

        Args:
            instance_name (str): name
            data (str): data

        Returns:
            bool: written or not
        """
        return self.redis_client.set(self.get_key(instance_name), data)

    def delete(self, instance_name):
        """
        delete all instance related keys

        Args:
            instance_name (str): name

        Returns:
            bool
        """
        keys = self.get_instance_keys(instance_name)
        if keys:
            return self.redis_client.delete(*keys)
        return True
