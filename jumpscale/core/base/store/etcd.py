import etcd3
import json

from . import ConfigNotFound, EncryptedConfigStore, EncryptionMode

from .serializers import JsonSerializer


class EtcdStore(EncryptedConfigStore):
    """
    EtcdStore store is an EncryptedConfigStore

    It saves the data in etcd and configuration for etcd comes from `config_env.get_store_config("etcd")`
    """

    def __init__(self, location):
        """
        create a new etcd store, the location given will be used to generate keys

        this keys will be combined to get/set instance config

        Args:
            location (Location)
        """
        super().__init__(location, JsonSerializer())
        etcd_config = self.config_env.get_store_config("etcd")
        hostname = etcd_config.get("hostname", "localhost")
        port = etcd_config.get("port", 2379)
        self.etcd_client = etcd3.client(host=hostname, port=port)

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
        read instance config from etcd

        Args:
            instance_name (name): name

        Returns:
            str: return json object
        """
        key = self.get_key(instance_name)
        if not self.etcd_client.get(key)[0]:
            raise ConfigNotFound(f"cannot find config for {instance_name} at {key}")

        return json.loads(self.etcd_client.get(key)[0].decode())

    def get(self, instance_name):
        """
        get instance config from etcd

        Args:
            instance_name (name): name

        Returns:
            instance: return config object
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
        key = self.get_key(instance_name)
        self.etcd_client.put(key, data)

    def list_all(self):
        """
        get all names of instances (instance keys)

        Returns:
            List[str]: list of instance names
        """
        return [item[1].key.decode().split(".")[-1] for item in self.etcd_client.get_all()]

    def delete(self, instance_name):
        """
        delete given instance

        Args:
            instance_name (str): name

        Returns:
            bool
        """
        key = self.get_key(instance_name)
        return self.etcd_client.delete(key)
