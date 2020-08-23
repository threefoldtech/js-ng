"""
Store defines the interface for the backend storage, let it be filesystem or redis.

This module also defines the abstractions needed for any storage backend.

Every backend should be able to organize configuration for multiple instance given a location, also
read/write the config data in raw (string) format.
"""


import os

from abc import ABC, abstractmethod
from enum import Enum

from jumpscale.data.nacl import NACL
from jumpscale.data.serializers import base64
from jumpscale.core.config import Environment


# we will use this as a key field name to get it when searching
KEY_FIELD_NAME = "instance_name_"


class InvalidPrivateKey(Exception):
    """
    raised when the private key configured is invalid
    """


class StoreException(Exception):
    """
    raised by store backends
    """


class ConfigNotFound(Exception):
    """
    raised when a config is not found for an instance
    """


class Location:
    """
    dot-separated auto-location for any type

    for example, if we have a class in jumpscale/clients/redis/<type>
    location name will be jumpscale.clients.redis.<type>
    """

    def __init__(self, *name_list, type_=None):
        self.type = type_
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

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


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
    - `find(self, cursor_=None, limit_=None, **query)`: optional search method with query as field mapping
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
    def find(self, cursor_=None, limit_=None, **query):
        pass

    @abstractmethod
    def delete(self, instance_name):
        pass


class EncryptedConfigStore(ConfigStore, EncryptionMixin):
    """the base class for any config store backend"""

    def __init__(self, location, serializer):
        """
        the base for encrypted config store

        Args:
            location (Location)
            serializer (Serializer)

        Raises:
            InvalidPrivateKey: in case the private key is not configured
        """
        self.location = location
        self.serializer = serializer
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
        config = self.serializer.deserialize(self.read(instance_name))
        return self._process_config(config, EncryptionMode.Decrypt)

    def find(self, cursor_=None, limit_=None, **query):
        """
        a generic find, which do a linear search over all items

        if you want a better way, use a store which provides search

        Args:
            cursor_ (any, optional): an optional cursor, to start searching from. Defaults to None.
            limit_ (int, optional): results limit. Defaults to None.
            query: a mapping between field and value fo search by

        Returns:
            tuple: the new cursor, total result count and a generator for results
        """
        all_names = self.list_all()
        if not all_names:
            # empty result
            return cursor_, 0, (name for name in all_names)

        all_count = len(all_names)
        if not limit_:
            limit_ = all_count

        start_search = not bool(cursor_)
        found = []

        for index in range(all_count):
            instance_name = all_names[index]
            if instance_name == cursor_:
                start_search = True

            if not start_search:
                continue

            data = self.get(instance_name)
            for name, value in query.items():
                if name in data:
                    data[KEY_FIELD_NAME] = instance_name
                    target_value = data[name]
                    if isinstance(target_value, str):
                        # just a simple normalization
                        value = str(value).lower()
                        target_value = target_value.lower()

                    if value == target_value and data not in found:
                        found.append(data)

            if len(found) >= limit_:
                break

        if index == all_count - 1:
            new_cursor = None
        else:
            new_cursor = all_names[index + 1]

        # return the new cursor, total found and a generator
        return new_cursor, len(found), (config for config in found)

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
        return self.write(instance_name, self.serializer.serialize(new_config))
