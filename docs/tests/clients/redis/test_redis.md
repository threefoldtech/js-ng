### test01_get_redis_client_0

Test case for getting redis client with/without password [with password=False].

**Test Scenario**

- Start redis server with/without password.
- Get client for redis.
- Try to set and get a random variable.

### test01_get_redis_client_1

Test case for getting redis client with/without password [with password=True].

**Test Scenario**

- Start redis server with/without password.
- Get client for redis.
- Try to set and get a random variable.

### test_02_is_running

Test case for Checking redis is running.

**Test Scenario**

- Get redis client before starting the server.
- Check that redis server is not running.
- Start redis server.
- Get client for redis.
- Check that the redis server is running.
