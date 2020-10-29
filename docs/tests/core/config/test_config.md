### test_01_get_default_config

Test case for getting jsng default config.

**Test Scenario**

- Get the default config.
- Check that some of these config are having the default values.

### test_02_get_config

Test case for getting jsng config.

**Test Scenario**

- Get the config.
- Check that some of these config keys are exist.

### test_03_update_config

Test case for updating jsng config.

**Test Scenario**

- Set a new key with random value.
- Get the value this key.
- Check that the value of this key is the same has been set.
- Get the config.
- Remove this key from the config and update the config.

### test_04_migrate_config

Test case for migrating config.

**Test Scenario**

- Get the config.
- Remove factory key.
- Migrate the config.
- Get the new config.
- Update the config to the original one.
- Check that the factory key is in the new config.

### test_05_generate_key

Test case for generating key.

**Test Scenario**

- Create a temporary directory.
- Generate a key in the this directory.
- Check that the key has been generated.
- Remove this directory.

### test_06_get_environment_config_0_logging_config

Test case for getting environment config [with config_name='logging_config'].

**Test Scenario**

- Get the config.
- Get environment config.
- Check that the environment config is the same as the one used in config.

### test_06_get_environment_config_1_private_key

Test case for getting environment config [with config_name='private_key'].

**Test Scenario**

- Get the config.
- Get environment config.
- Check that the environment config is the same as the one used in config.

### test_06_get_environment_config_2_private_key_path

Test case for getting environment config [with config_name='private_key_path'].

**Test Scenario**

- Get the config.
- Get environment config.
- Check that the environment config is the same as the one used in config.

### test_06_get_environment_config_3_threebot_data

Test case for getting environment config [with config_name='threebot_data'].

**Test Scenario**

- Get the config.
- Get environment config.
- Check that the environment config is the same as the one used in config.

### test_07_get_store_config

Test case for getting store config.

**Test Scenario**

- Get the config.
- Get store config.
- Check that the store config is the same as the one used in config.
- Try to get store config for random store name, should raise error.
