import copy

from jumpscale.loader import j
from parameterized import parameterized
from tests.base_tests import BaseTests


class TestConfig(BaseTests):
    def test_01_get_default_config(self):
        """Test case for getting jsng default config.

        **Test Scenario**

        - Get the default config.
        - Check that some of these config are having the default values.
        """
        self.info("Get the default config.")
        default_config = j.core.config.get_default_config()

        self.info("Check that some of these config are having the default values.")
        self.assertEqual(default_config.get("store"), "filesystem")
        self.assertEqual(default_config.get("factory"), {"always_reload": False})
        self.assertEqual(default_config.get("alerts"), {"enabled": True, "level": 40})

    def test_02_get_config(self):
        """Test case for getting jsng config.

        **Test Scenario**

        - Get the config.
        - Check that some of these config keys are exist.
        """
        self.info("Get the config.")
        config = j.core.config.get_config()

        self.info("Check that some of these config keys are exist.")
        self.assertTrue(config.get("store"))
        self.assertTrue(config.get("factory"))
        self.assertTrue(config.get("alerts"))

    def test_03_update_config(self):
        """Test case for updating jsng config.

        **Test Scenario**

        - Set a new key with random value.
        - Get the value this key.
        - Check that the value of this key is the same has been set.
        - Get the config.
        - Remove this key from the config and update the config.
        """
        self.info("Set a new key with random value.")
        key = self.generate_random_text()
        value = self.generate_random_text()
        j.core.config.set(key, value)

        self.info("Get the value this key.")
        result = j.core.config.get(key)

        self.info("Check that the value of this key is the same has been set.")
        self.assertEqual(result, value)

        self.info("Get the config.")
        config = j.core.config.get_config()

        self.info("Remove this key from the config and update the config.")
        config.pop(key)
        j.core.config.update_config(config)

    def test_04_migrate_config(self):
        """Test case for migrating config.

        **Test Scenario**

        - Get the config.
        - Remove factory key.
        - Migrate the config.
        - Get the new config.
        - Update the config to the original one.
        - Check that the factory key is in the new config.
        """
        self.info("Get the config.")
        original_config = j.core.config.get_config()

        self.info("Remove factory key.")
        config = copy.deepcopy(original_config)
        config.pop("factory")
        j.core.config.update_config(config)

        self.info("Migrate the config.")
        j.core.config.config.migrate_config()

        self.info("Get the new config.")
        new_config = j.core.config.get_config()

        self.info("Update the config to the original one.")

        j.core.config.update_config(original_config)

        self.info("Check that the factory key is in the new config.")
        self.assertIn("factory", new_config.keys())

    def test_05_generate_key(self):
        """Test case for generating key.

        **Test Scenario**

        - Create a temporary directory.
        - Generate a key in the this directory.
        - Check that the key has been generated.
        - Remove this directory.
        """
        self.info("Create a temporary directory.")
        dir_path = j.sals.fs.join_paths("/tmp", self.generate_random_text())
        j.sals.fs.mkdir(dir_path)

        self.info("Generate a key in the this directory.")
        key_file_path = j.sals.fs.join_paths(dir_path, self.generate_random_text())
        j.core.config.config.generate_key(key_file_path)

        self.info("Check that the key has been generated.")
        self.assertTrue(j.sals.fs.exists(f"{key_file_path}.priv"))
        self.assertTrue(j.sals.fs.exists(f"{key_file_path}.pub"))

        self.info("Remove this directory.")
        j.sals.fs.rmtree(dir_path)

    @parameterized.expand(["logging_config", "private_key", "private_key_path", "threebot_data"])
    def test_06_get_environment_config(self, config_name):
        """Test case for getting environment config.

        **Test Scenario**

        - Get the config.
        - Get environment config.
        - Check that the environment config is the same as the one used in config.
        """
        self.info("Get the config.")
        config = j.core.config.get_config()

        self.info("Get environment config.")
        env = j.core.config.Environment()
        conf = getattr(env, f"get_{config_name}")

        self.info("Check that the environment config is the same as the one used in config.")
        if config_name == "private_key":
            priv_key_path = config.get("private_key_path")
            result = j.sals.fs.read_binary(priv_key_path)
        elif config_name == "logging_config":
            result = config.get("logging")
        elif config_name == "threebot_data":
            result = config.get("threebot")
        else:
            result = config.get(config_name)

        self.assertEqual(result, conf())

    def test_07_get_store_config(self):
        """Test case for getting store config.

        **Test Scenario**

        - Get the config.
        - Get store config.
        - Check that the store config is the same as the one used in config.
        - Try to get store config for random store name, should raise error.
        """
        self.info("Get the config.")
        config = j.core.config.get_config()

        self.info("Get store config.")
        env = j.core.config.Environment()
        filesystem = env.get_store_config("filesystem")
        redis = env.get_store_config("redis")
        whoosh = env.get_store_config("whoosh")

        self.info("Check that the store config is the same as the one used in config.")
        self.assertEqual(filesystem, config.get("stores").get("filesystem"))
        self.assertEqual(redis, config.get("stores").get("redis"))
        self.assertEqual(whoosh, config.get("stores").get("whoosh"))

        self.info("Try to get store config for random store name, should raise error.")
        with self.assertRaises(Exception):
            env.get_store_config(self.generate_random_text())
