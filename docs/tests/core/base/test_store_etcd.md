### test_01_create_find_models

Test for creating, finding and deleting models.

**Test Scenario**

- Create model and save it.
- List all instances and check that only one instance found.
- Get the instance and check that all fields are stored.

### test_02_create_more_instance

Test for creating more than one instance.

**Test Scenario**

- Create three instances.
- Check that the instance are stored in etcd.
- List all instances and check that three instance found.
