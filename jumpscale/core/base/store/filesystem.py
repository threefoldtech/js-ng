import os

from . import ConfigNotFound, EncryptedConfigStore
from .serializers import JsonSerializer

from jumpscale.sals.fs import exists, make_path, read_file_binary, rmtree, write_file_binary


class FileSystemStore(EncryptedConfigStore):
    """
    Filesystem store is an EncryptedConfigStore

    It saves the config relative to `config_env.get_store_config("filesystem")`

    To store every instance config in a different path, it uses the given `Location`.
    """

    def __init__(self, location):
        """
        create a new `FileSystemStore` that stores config at the given location under configured root.

        The root directory can be configured, see `jumpscale.core.config`

        Args:
            location (Location): where config will be stored per instance
        """
        super(FileSystemStore, self).__init__(location, JsonSerializer())
        self.root = self.config_env.get_store_config("filesystem")["path"]

    @property
    def config_root(self):
        """
        get the root directory where all configurations are written

        Returns:
            str: path
        """
        return os.path.join(self.root, self.location.path)

    def get_instance_root(self, instance_name):
        """
        get the directory where instance config is written

        Args:
            instance_name (str): name

        Returns:
            str: path
        """
        return os.path.join(self.config_root, instance_name)

    def get_path(self, instance_name):
        """
        get the path to data file where instance config is written

        Args:
            instance_name (str): name

        Returns:
            str: path
        """
        return os.path.join(self.get_instance_root(instance_name), "data")

    def read(self, instance_name):
        """
        read config data from the data file

        Args:
            instance_name (str): name

        Returns:
            str: data
        """
        path = self.get_path(instance_name)
        if not exists(path):
            raise ConfigNotFound(f"cannot find config for {instance_name} at {path}")
        return read_file_binary(path)

    def list_all(self):
        """
        list all instance names (directories under config root)

        Returns:
            list: instance/directory names
        """
        if not os.path.exists(self.config_root):
            return []
        return os.listdir(self.config_root)

    def write(self, instance_name, data):
        """
        write config data to data file

        Args:
            instance_name (str): config
            data (str): data

        Returns:
            bool: written or not
        """
        path = self.get_path(instance_name)
        make_path(path)
        return write_file_binary(path, data.encode())

    def delete(self, instance_name):
        """
        delete instance config directory

        Args:
            instance_name (str):
        """
        path = self.get_instance_root(instance_name)
        if os.path.exists(path):
            rmtree(path)
