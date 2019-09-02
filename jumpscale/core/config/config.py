import os

import nacl.utils
import nacl.encoding
import pytoml as toml

from nacl.public import PrivateKey, Box


__all__ = ["config_path", "config_root", "get_default_config", "get_config", "update_config", "Environment"]


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
        "stores": {
            "redis": {"hostname": "localhost", "port": 6379},
            "filesystem": {"path": os.path.expanduser(os.path.join(config_root, "secureconfig"))},
        },
        "store": "filesystem",
    }


def get_config():
    with open(config_path, "r") as f:
        return toml.load(f)


def update_config(data):
    with open(config_path, "w") as f:
        toml.dump(data, f)


def migrate_config():
    """add missing top level keys to current config from default"""

    default_config = get_default_config()
    current_config = get_config()

    for key, value in default_config.items():
        if key not in current_config:
            current_config[key] = value

    update_config(current_config)


if not os.path.exists(config_path):
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    os.mknod(config_path)


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


class StoreTypeNotFound(Exception):
    pass


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

    def get_store_config(self, name):
        config = get_config()
        stores = config["stores"]
        if name not in stores:
            raise StoreTypeNotFound(f"'{name}' store is not found")
        return stores[name]


migrate_config()
