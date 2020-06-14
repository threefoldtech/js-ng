import redis

from . import EncryptedConfigStore


class RedisStore(EncryptedConfigStore):
    """
    RedisStore store is an EncryptedConfigStore

    It saves the data in redis and configuration for redis comes from `config_env.get_store_config("redis")`
    """

    def __init__(self, location):
        """
        create a new redis store, the location given will be used to generate keys

        this keys will be combined to get/set instance config

        Args:
            location (Location)
        """
        super().__init__(location)
        redis_config = self.config_env.get_store_config("redis")
        self.redis_client = redis.Redis(redis_config["hostname"], redis_config["port"])

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
        read instance config from redis

        Args:
            instance_name (name): name

        Returns:
            str: data
        """
        return self.redis_client.get(self.get_key(instance_name))

    def _full_scan(self, pattern):
        """
        get the full result of a scan command on current redis database by this pattern

        Args:
            pattern ([type]): [description]
        """
        keys = []
        cursor, values = self.redis_client.scan(0, pattern)

        while values:
            keys += values
            if not cursor:
                break
            cursor, values = self.redis_client.scan(cursor, pattern)

        return keys

    def get_location_keys(self):
        """
        get all keys under current location (scanned)

        Returns:
            list: a list of keys
        """
        return self._full_scan(f"{self.location.name}.*")

    def get_instance_keys(self, instance_name):
        """
        get all instance related keys (scanned)

        Args:
            instance_name (str): name

        Returns:
            list: list of keys
        """
        return self._full_scan(f"{self.location.name}.{instance_name}*")

    def list_all(self):
        """
        get all names of instances (instance keys)

        Returns:
            [type]: [description]
        """
        names = []

        keys = self.get_location_keys()
        for key in keys:
            # remove location name part
            name = key.decode().replace(self.location.name, "").lstrip(".")
            if "." not in name:
                names.append(name)
        return names

    def write(self, instance_name, data):
        """
        set data with the corresponding key for this instance

        Args:
            instance_name (str): name
            data (str): data

        Returns:
            bool: written or not
        """
        return self.redis_client.set(self.get_key(instance_name), data)

    def delete(self, instance_name):
        """
        delete all instance related keys

        Args:
            instance_name (str): name

        Returns:
            bool
        """
        keys = self.get_instance_keys(instance_name)
        if keys:
            return self.redis_client.delete(*keys)
        return True
