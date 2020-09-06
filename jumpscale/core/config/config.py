"""Config module is the single entry of configurations across the framework.

It allows
- resolving configurations paths for configuration directory`config_root`, or configuration file path `config_path`
- rebuildling default configurations or retrieving them (using `get_default_config`)
- Getting configurations using `get_default_config`
- Updating configuration using `update_config`



JS-NG> j.core.config
<module 'jumpscale.core.config' from '/home/ahmed/wspace/js/js-ng/jumpscale/core/config/__init__.py'>

## Getting where is the config.toml path
```
JS-NG> j.core.config.config_path
'/home/ahmed/.config/jumpscale/config.toml'
```

## Getting configuration directory
```
JS-NG> j.core.config.config_root
'/home/ahmed/.config/jumpscale'
```

## Getting default configurations of js-ng (used in case of no configuration found)
```
JS-NG> j.core.config.get_default_config()
{'debug': True, 'logging': {'redis': {'enabled': True, 'level': 15, 'max_size': 1000, 'dump': True, 'dump_dir': '/home/ahmed/.config/jumpscale/logs/redis'}, 'filesystem': {'enabled': True, 'level': 15, 'log_dir': '/home/ahmed/.config/jumpscale/logs/fs/log.txt', 'rotation': '5 MB'}}, 'alerts': {'enabled': True, 'level': 40}, 'ssh_key_path': '', 'private_key_path': '', 'stores': {'redis': {'hostname': 'localhost', 'port': 6379}, 'filesystem': {'path': '/home/ahmed/.config/jumpscale/secureconfig'}}, 'store': 'filesystem', 'threebot': {'default': ''}, 'explorer': {'default_url': 'https://explorer.testnet.grid.tf/explorer'}}
```

## Getting the current configurations
```
JS-NG> j.core.config.get_config()
{'debug': True, 'ssh_key_path': '', 'log_to_redis': False, 'log_to_files': True, 'log_level': 15, 'private_key_path': '/home/ahmed/.config/jumpscale/mykey.priv', 'secure_config_path': '/home/ahmed/.config/jumpscale/secureconfig', 'store': 'filesystem', 'logging': {'handlers': [{'sink': 'sys.stdout', 'format': '{time} - {message}', 'colorize': True, 'enqueue': True}, {'sink': '/home/ahmed/.config/jumpscale/logs/file_jumpscale.log', 'serialize': True, 'enqueue': True}], 'redis': {'enabled': True, 'level': 15, 'max_size': 1000, 'dump': True, 'dump_dir': '/home/ahmed/.config/jumpscale/logs/redis'}, 'filesystem': {'enabled': True, 'level': 15, 'log_dir': '/home/ahmed/.config/jumpscale/logs/fs/log.txt', 'rotation': '5 MB'}}, 'stores': {'redis': {'hostname': 'localhost', 'port': 6379}, 'filesystem': {'path': '/home/ahmed/.config/jumpscale/secureconfig'}}, 'alerts': {'enabled': True, 'level': 40}, 'threebot': {'default': ''}, 'explorer': {'default_url': 'https://explorer.testnet.grid.tf/explorer'}}
```

## Updating configurations

```
JS-NG> conf = j.core.config.get_default_config()
JS-NG> conf
{'debug': True, 'ssh_key_path': '', 'log_to_redis': False, 'log_to_files': True, 'log_level': 15, 'private_key_path': '/home/ahmed/.config/jumpscale/mykey.priv', 'secure_config_path': '/home/ahmed/.config/jumpscale/secureconfig', 'store': 'filesystem', 'logging': {'handlers': [{'sink': 'sys.stdout', 'format': '{time} - {message}', 'colorize': True, 'enqueue': True}, {'sink': '/home/ahmed/.config/jumpscale/logs/file_jumpscale.log', 'serialize': True, 'enqueue': True}], 'redis': {'enabled': True, 'level': 15, 'max_size': 1000, 'dump': True, 'dump_dir': '/home/ahmed/.config/jumpscale/logs/redis'}, 'filesystem': {'enabled': True, 'level': 15, 'log_dir': '/home/ahmed/.config/jumpscale/logs/fs/log.txt', 'rotation': '5 MB'}}, 'stores': {'redis': {'hostname': 'localhost', 'port': 6379}, 'filesystem': {'path': '/home/ahmed/.config/jumpscale/secureconfig'}}, 'alerts': {'enabled': True, 'level': 40}, 'threebot': {'default': ''}, 'explorer': {'default_url': 'https://explorer.testnet.grid.tf/explorer'}}

JS-NG> conf['favcolor'] = 'blue'
JS-NG> j.core.config.update_config(conf)
JS-NG> j.core.config.get_config()
{'debug': True, 'ssh_key_path': '', 'log_to_redis': False, 'log_to_files': True, 'log_level': 15, 'private_key_path': '/home/ahmed/.config/jumpscale/mykey.priv', 'secure_config_path': '/home/ahmed/.config/jumpscale/secureconfig', 'store': 'filesystem', 'favcolor': 'blue', 'logging': {'handlers': [{'sink': 'sys.stdout', 'format': '{time} - {message}', 'colorize': True, 'enqueue': True}, {'sink': '/home/ahmed/.config/jumpscale/logs/file_jumpscale.log', 'serialize': True, 'enqueue': True}], 'redis': {'enabled': True, 'level': 15, 'max_size': 1000, 'dump': True, 'dump_dir': '/home/ahmed/.config/jumpscale/logs/redis'}, 'filesystem': {'enabled': True, 'level': 15, 'log_dir': '/home/ahmed/.config/jumpscale/logs/fs/log.txt', 'rotation': '5 MB'}}, 'stores': {'redis': {'hostname': 'localhost', 'port': 6379}, 'filesystem': {'path': '/home/ahmed/.config/jumpscale/secureconfig'}}, 'alerts': {'enabled': True, 'level': 40}, 'threebot': {'default': ''}, 'explorer': {'default_url': 'https://explorer.testnet.grid.tf/explorer'}}
```

## Get/Set
you can use `j.core.config.get` and `j.core.config.set` to retrive values of keys or set the value of a key respectively.

e.g

```
JS-NG> j.core.config.get("favcolor")
'blue'

JS-NG> j.core.config.set("favcolor", "grey")
JS-NG> j.core.config.get("favcolor")
'grey'
```


"""

import os

import nacl.utils
import nacl.encoding
import pytoml as toml
from nacl.public import PrivateKey


__all__ = [
    "config_path",
    "config_root",
    "get_default_config",
    "get_config",
    "update_config",
    "Environment",
    "get",
    "set",
    "set_default",
    "get_current_version",
]

__version__ = "11.0.0-a3"


config_root = os.path.expanduser(os.path.join("~/.config", "jumpscale"))
config_path = os.path.join(config_root, "config.toml")


def get_current_version():
    return __version__


def get_default_config():
    """retrieves default configurations for plain jumpscale

    Returns:
        dict: default configuration
    """
    return {
        "debug": True,
        "shell": "ptpython",
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
            "whoosh": {"path": os.path.expanduser(os.path.join(config_root, "whoosh_indexes"))},
        },
        "factory": {"always_reload": False},
        "store": "filesystem",
        "threebot": {"default": "",},
        "explorer": {"default_url": "https://explorer.testnet.grid.tf/explorer",},
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


def get(key, default=None):
    """ Retrives value from jumpscale config

    Arguments:
        key (str): the key you wish to retrieve
        default (object): return value if key doesn't exist in configurations
    """
    conf = get_config()
    return conf.get(key, default)


def set(key, val):
    """ Sets value in jumpscale config

    Arguments:
        key (str): the key you wish to update
        val: value to update with
    """
    conf = get_config()
    conf[key] = val
    update_config(conf)


def set_default(key, val):
    """ Sets key to value in jumpscale config and returns 

    Arguments:
        key (str): the key you wish to update
        val: value to update with and to return if key doesn't exist in configurations
    
    Returns:
        val (str): returned if key doesn't exist in configuration or the value of key in configurations
    """
    conf = get_config()
    if key in conf:
        return conf[key]
    else:
        set(key, val)
        return val




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
        # don't ues mknod https://github.com/threefoldtech/js-ng/issues/182
        f.close()


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
