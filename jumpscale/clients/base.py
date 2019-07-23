import os
from secretconf import read_config, save_config
from jumpscale.core.config import JumpscaleConfigEnvironment


class InvalidPrivateKey(Exception):
    pass

class SecureConfigSource:

    def __init__(self, obj):
        self.owner = obj
        self._instance_name = obj.instance_name
        self._client_name = obj.__class__.__name__.lower()

    @property
    def client_name(self):
        return self._client_name

    @property
    def instance_name(self):
        return self._instance_name

    def set_appconfig(self, appconfigenv):
        self._appconfigenv = appconfigenv

    @property
    def instance_config_path(self):
        return self._get_instance_config_path()
        
    def _get_instance_config_path(self):
        instance_filename = "{}__{}".format(self.client_name, self.instance_name)
        return os.path.join(self._appconfigenv.get_secure_config_path(), instance_filename)

    def _get_instance_config(self):
        if not os.path.exists(self.instance_config_path):
            os.makedirs(os.path.dirname(self.instance_config_path), exist_ok=True)
            os.mknod(self.instance_config_path)
        if not self._appconfigenv:
            raise InvalidPrivateKey()

        return read_config(self.instance_name, self.instance_config_path, self._appconfigenv.get_private_key())
    
    def _save_config(self, data):
        if not self._appconfigenv:
            raise InvalidPrivateKey()

        return save_config(self.instance_name, data, self.instance_config_path, self._appconfigenv.get_private_key())
    
    @property
    def data(self):
        try:
            return self._get_instance_config()[self.instance_name]
        except Exception:
            return {}
    
    @data.setter
    def data(self, data):
        return self._save_config(data)


class SecureClient:
    def __init__(self, client):
        self.config = SecureConfigSource(client)
        self.config.set_appconfig(JumpscaleConfigEnvironment())

