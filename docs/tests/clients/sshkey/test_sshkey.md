### test01_check_public_path

Test case for checking sshkey public path.

**Test Scenario**
- Get a sshkey.
- Check sshkey public path.

### test02_check_generate_keys

Test case for generating keys.

**Test Scenario**
- Get a sshkey.
- Generate keys.
- Check that the public key has been generated belongs to the private key.

### test03_check_generate_keys_with_wrong_path

Test case for generating keys with wrong private key path.

**Test Scenario**
- Get a sshkey.
- Set private key to wrong path.
- Try to generate keys with wrong path it should raise an error.

### test04_check_write_to_filesystem

Test case for writing keys to file system.

**Test Scenario**
- Get a sshkey.
- Generate keys.
- Set private key path.
- Writing keys to file system.
- Checking that keys has been written.

### test05_load_from_filesystem

Test case for loading keys from file system.

**Test Scenario**
- Get a sshkey.
- Generate keys.
- Create a new sshkey.
- Load keys from file system.
- Check that keys has been loaded.
