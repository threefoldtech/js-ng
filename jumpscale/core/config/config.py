"""Config modules is the single entry of configurations across the framework.
It allows
- resolving configurations paths for configuration directory`config_root`, or configuration file path `config_path`
- rebuildling default configurations or retrieving them (using `get_default_config`)
- Getting configurations using `get_default_config`
- Updating configuration using `update_config`

"""

import os

import nacl.utils
import nacl.encoding
import pytoml as toml
from jumpscale.data.encryption import mnemonic

from nacl.public import PrivateKey, Box


__all__ = [
    "config_path",
    "config_root",
    "get_default_config",
    "get_config",
    "update_config",
    "Environment",
    "configure_threebot",
]


config_root = os.path.expanduser(os.path.join("~/.config", "jumpscale"))
config_path = os.path.join(config_root, "config.toml")


def get_default_config():
    """retrieves default configurations for plain jumpscale

    Returns:
        e.g return
        ```
        {
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
        "threebot": {
            "name": "",
            "id": 0,
            "explorer_url": "https://explorer.testnet.grid.tf/explorer",
            "private_key": "",
            "email": "",
        },
       }```
    """
    return {
        "debug": True,
        "logging": {
            "redis": {
                "enabled": True,
                "level": 15,
                "max_size": 1000,
                "dump": True,
                "dump_dir": os.path.join(config_root, "logs/redis"),
            },
            "filesystem": {
                "enabled": True,
                "level": 15,
                "log_dir": os.path.join(config_root, "logs/fs/log.txt"),
                "rotation": "5 MB",
            },
        },
        "alerts": {"enabled": True, "level": 40},
        "ssh_key_path": "",
        "private_key_path": "",
        "stores": {
            "redis": {"hostname": "localhost", "port": 6379},
            "filesystem": {"path": os.path.expanduser(os.path.join(config_root, "secureconfig"))},
        },
        "store": "filesystem",
        "threebot": {
            "name": "",
            "id": 0,
            "explorer_url": "https://explorer.testnet.grid.tf/explorer",
            "private_key": "",
            "email": "",
        },
    }


def get_config():
    """Gets jumpscale configurations

    Returns:
        [dict] - toml loaded config of CONFIG_DIR/config.toml
    """
    with open(config_path, "r") as f:
        return toml.load(f)


def update_config(data):
    """Update jumpscale config with new data

    Arguments:
        data {dict} -- dict to update the config with.
    """
    with open(config_path, "w") as f:
        toml.dump(data, f)


def migrate_config():
    """add missing keys to current config from default"""

    default_config = get_default_config()
    current_config = get_config()

    def copy_missing(default, current):
        for key, value in default.items():
            if key not in current:
                current[key] = value
            elif isinstance(value, dict):
                copy_missing(value, current[key])

    copy_missing(default_config, current_config)
    update_config(current_config)


# Create default configurations file on loading.
if not os.path.exists(config_path):
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w") as f:
        # don't ues mknod https://github.com/js-next/js-ng/issues/182
        f.close()


def generate_key(basepath):
    # seed = mnemonic.mnemonic_to_key(words)
    # hsk = PrivateKey(seed)
    hsk = PrivateKey.generate()
    hpk = hsk.public_key
    skpath = basepath + ".priv"
    pkpath = basepath + ".pub"
    with open(skpath, "wb") as f:
        f.write(hsk.encode(nacl.encoding.Base64Encoder()))
    with open(pkpath, "wb") as f:
        f.write(hpk.encode(nacl.encoding.Base64Encoder()))
    return skpath


def configure_threebot(name, email, wordsfile):
    with open(wordsfile) as wf:
        words = wf.read()

    seed = mnemonic.mnemonic_to_key(words.strip())
    hsk = PrivateKey(seed)
    priv_key = hsk.encode(nacl.encoding.Base64Encoder).decode()
    config = get_config()
    default_config = get_default_config()
    config["threebot"] = default_config["threebot"]
    config["threebot"].update({"private_key": priv_key, "name": name, "email": email})
    update_config(config)


class StoreTypeNotFound(Exception):
    pass


class Environment:
    def get_private_key_path(self):
        config = get_config()
        private_key_path = config["private_key_path"]
        return private_key_path

    def get_threebot_data(self):
        config = get_config()
        return config.get("threebot", {})

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

    def get_logging_config(self):
        return get_config()["logging"]


migrate_config()
