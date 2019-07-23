import os
import pytoml as toml


__all__ = ['config_path', 'js_default_config', 'get_jumpscale_config', 'update_jumpscale_config', 'JumpscaleConfigEnvironment']

config_path = os.path.expanduser(os.path.join("~/.config", "jumpscale", "config.toml"))

def js_default_config():
    return {
        "debug": True,
        "ssh_key_path": "",
        "log_to_redis": False,
        "log_to_files": True,
        "log_level": 15,
        "private_key_path": "",
        "secure_config_path": os.path.expanduser(os.path.join("~/.config", "jumpscale", "secureconfig")),
    }

if not os.path.exists(config_path):
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w") as f:
        toml.dump(js_default_config(), f)

def get_jumpscale_config():
    with open(config_path, "r") as f:
        return toml.load(f)

def update_jumpscale_config(data):
    with open(config_path, "w") as f:
        toml.dump(data, f)


class JumpscaleConfigEnvironment:
    def get_private_key_path(self):
        config = get_jumpscale_config()
        private_key_path = config['private_key_path']
        return private_key_path
    
    def get_private_key(self):
        return open(self.get_private_key_path(), "rb").read()

    def get_secure_config_path(self):
        config = get_jumpscale_config()
        secure_config_path = config['secure_config_path']
        return os.path.expanduser(secure_config_path)

