import copy
import json

import pymongo

from . import ConfigNotFound, EncryptedConfigStore, EncryptionMode
from .serializers import JsonSerializer


class MongoStore(EncryptedConfigStore):
    """
    MongoStore store is an EncryptedConfigStore

    It saves the data in mongo and configuration for mongo comes from `config_env.get_store_config("mongo")`
    """

    def __init__(self, location):
        """
        create a new mongo store, the location given will be used to generate keys

        this keys will be combined to get/set instance config

        Args:
            location (Location)
        """
        super().__init__(location, JsonSerializer())
        mongo_config = self.config_env.get_store_config("mongo")
        hostname = mongo_config.get("hostname", "localhost")
        port = mongo_config.get("port", 27017)
        self.mongo_client = pymongo.MongoClient(f"mongodb://{hostname}:{port}/")
        self._db = self.mongo_client["jsng"]
        self._col = self._db[location.name]

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
        read instance config from mongo

        Args:
            instance_name (name): name

        Returns:
            str: data
        """
        key = self.get_key(instance_name)
        query = {"++key++": key}
        res = list(self._col.find(query))
        if not res:
            raise ConfigNotFound(f"cannot find config for {instance_name} at {key}")
        ## TODO: should raise if there're more with the same ++key++
        return res[0]

    def get_location_keys(self):
        """
        get all keys under current location (scanned)

        Returns:
            list: a list of keys
        """
        return list(self._col.find({}, {"++key++": 1}))

    def list_all(self):
        """
        get all names of instances (instance keys)

        Returns:
            [type]: [description]
        """
        names = [r["++key++"].replace(self.location.name, "").lstrip(".") for r in self.get_location_keys()]

        return names

    def get(self, instance_name):
        """
        get instance config

        Args:
            instance_name (str): instance name

        Returns:
            dict: instance config as dict
        """
        config = self.read(instance_name)
        return self._process_config(config, EncryptionMode.Decrypt)

    def write(self, instance_name, data):
        """
        set data with the corresponding key for this instance

        Args:
            instance_name (str): name
            data (str): data

        Returns:
            bool: written or not
        """
        newdata = json.loads(data)
        newdata["++key++"] = self.get_key(instance_name)
        return self._col.insert_one(newdata)

    def delete(self, instance_name):
        """
        delete given instance

        Args:
            instance_name (str): name

        Returns:
            bool
        """
        return self._col.delete_one({"++key++": self.get_key(instance_name)})
