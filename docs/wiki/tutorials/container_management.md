# Container Management
## Getting docker client
```
dcl = j.clients.docker.new("mydocker_client") 
```
## Running a docker container
```
dcl.run("container_name", image="threefoldtech/js-ng")
```
## listing contaienrs
```
dcl.list(all=True) # lists all containers include stopped ones
```

## getting container
```
container = dcl.get(<container_id or name>)
```
## executing commmands
```
dcl.exec(<container_id>, "ls /tmp")
container.exec_run("ls /tmp)
```
## check if container exists
```
dcl.exists(<contaienr_id>)
```
## deleting a container
```
dcl.delete(<container_id>, force=True) # delete even if it is running
```
## killing docker container
```
dcl.kill(<container_id>, <kill signal>)
```
## restarting docker container
```
dcl.restart(<container_id>, timeout=20)
```
## starting docker container
```
dcl.start(<container_id>)
```
##
```
dcl.stop(<container_id>)
```
