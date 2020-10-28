### test01_docker_get

Test getting container.

**Test Scenario**

- Create docker container.
- Get container ID using container name.
- Try to get this container one time using container name.
- Try to get a container with a non valid name, and make sure that it raises an error.

### test02_docker_list

Test list docker.

**Test Scenario**

- Create the first docker.
- Check that the docker is created correctly.
- Get container ID using container name.
- Create the second docker.
- Try to list this container using list subcommand with option all=False to list only the running container.
- Check the output of list command.
- Use list subcommand with option all=True to list all containers.
- Check the output of list command and make sure that it lists the two containers.

### test03_docker_start

Test start docker.

**Test Scenario**

- Create docker container.
- Use start method to start docker container.
- Check that docker is started correctly.
- Use start method to start docker with non exist name, should raise an error.

### test04_docker_stop

Test start docker.

**Test Scenario**

- Create docker container.
- Check that the docker is running.
- Use stop method to stop docker container.
- Check that docker is stopped correctly.
- Use stop method to stop docker with non exist name, should raise an error.

### test05_docker_exec

Test exec docker.

**Test Scenario**

- Create a docker container.
- Use docker exec method to create file in /tmp.
- check that file has been created correctly.

### test06_docker_delete

Test delete docker.

**Test Scenario**

- Create a docker container.
- Check that the docker has been created and it's running correctly.
- Use delete method to delete the container, with option force=True to delete the running container.
- Check that the container has been deleted correctly.
- Create a stopped container.
- Check that the docker has been created correctly and it's a stopped docker.
- Try to delete the stopped docker using force=False should be deleted correctly.
- Check that the container has been deleted correctly.
- Create a running container.
- Check that the container has been created and it's running correctly.
- Try to delete the running docker using force=False option it should raise an error.

### test07_docker_run

Test run docker.

**Test Scenario**

- Create a docker with run command. With those options:
1. Add hostname using hostname option.
2. Add environmental variable.
- Check that the docker has been created correctly.
- Check the environmental variable is created correctly.
- Check that the hostname has been created correctly.

### test08_docker_create

Test run docker.

**Test Scenario**

- Create a docker with create method.
- Check that docker has been create successfully.
