import etcd3
import json

from . import ConfigNotFound, EncryptedConfigStore, EncryptionMode

from .serializers import JsonSerializer


class EtcdStore(EncryptedConfigStore):
    def __init__(self, location):
        super().__init__(location, JsonSerializer())
        etcd_config = self.config_env.get_store_config("etcd")
        hostname = etcd_config.get("hostname", "localhost")
        port = etcd_config.get("port", 2379)
        self.etcd_client = etcd3.client(host=hostname, port=port)

    def get_key(self, instance_name):
        return ".".join([self.location.name, instance_name])

    def read(self, instance_name):
        key = self.get_key(instance_name)
        if not self.etcd_client.get(instance_name)[0]:
            raise ConfigNotFound(f"cannot find config for {instance_name} at {key}")

        return self.etcd_client.get(key)[0]

    def get(self, instance_name):
        config = self.read(instance_name)
        return self._process_config(config, EncryptionMode.Decrypt)

    def write(self, instance_name, data):
        key = self.get_key(instance_name)
        self.etcd_client.put(key, data)
        "folder1.folder2.instance_name"

    def list_all(self):
        return [item[1].key.decode().split(".")[-1] for item in self.etcd_client.get_all()]

    def delete(self, instance_name):
        key = self.get_key(instance_name)
        return self.etcd_client.delete(key)

