import os
import pytoml as toml
import nacl.utils
from nacl.public import PrivateKey, Box
import nacl.encoding


__all__ = ["config_path", "get_default_config", "get_config", "update_config", "Environment"]


config_root = os.path.expanduser(os.path.join("~/.config", "jumpscale"))
config_path = os.path.join(config_root, "config.toml")


def get_default_config():
    return {
        "debug": True,
        "ssh_key_path": "",
        "logging": {"handlers": []},
        "log_to_redis": False,
        "log_to_files": True,
        "log_level": 15,
        "private_key_path": "",
        "secure_config_path": os.path.join(config_root, "secureconfig"),
    }


if not os.path.exists(config_path):
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w") as f:
        toml.dump(get_default_config(), f)


def get_config():
    with open(config_path, "r") as f:
        return toml.load(f)


def update_config(data):
    with open(config_path, "w") as f:
        toml.dump(data, f)


def generate_key(basepath):
    hsk = PrivateKey.generate()
    hpk = hsk.public_key
    skpath = basepath + ".priv"
    pkpath = basepath + ".pub"
    with open(skpath, "wb") as f:
        f.write(hsk.encode(nacl.encoding.Base64Encoder()))
    with open(pkpath, "wb") as f:
        f.write(hpk.encode(nacl.encoding.Base64Encoder()))
    return skpath


class Environment:
    def get_private_key_path(self):
        config = get_config()
        private_key_path = config["private_key_path"]
        return private_key_path

    def get_private_key(self):
        private_key_path = self.get_private_key_path()
        if not private_key_path:
            keypath = os.path.join(config_root, "privatekey")
            private_key_path = generate_key(keypath)
            config = get_config()
            config["private_key_path"] = private_key_path
            update_config(config)
        return open(private_key_path, "rb").read()

    def get_secure_config_path(self):
        config = get_config()
        secure_config_path = config["secure_config_path"]
        return os.path.expanduser(secure_config_path)

