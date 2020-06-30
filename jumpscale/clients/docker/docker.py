"""This module used to manage your conatiners, create ,run, list, delete and exec commands on docker
for example
```
#getting docker clinet
cl = j.clients.docker.get('test')
running docker
cl.run("container_name", "threefoldtech/js-ng")
# listing contaienrs
cl.list(all=True) # lists all containers include stopped ones
# getting container
container = cl.get(<container_id or name>)
executing commmands
cl.exec("container_id", "ls /tmp")
or container.exec_run("ls /tmp)
```
"""
import docker
from jumpscale.clients.base import Client
from jumpscale.core.base import fields


class DockerClient(Client):
    base_url = fields.String()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__client = None

    @property
    def client(self):
        if not self.__client:
            if self.base_url:
                self.__client = docker.DockerClient(base_url=self.base_url)
            else:
                self.__client = docker.from_env()
        return self.__client

    def create(
        self,
        name,
        image,
        command=None,
        environment=None,
        entrypoint=None,
        volumes=None,
        devices=None,
        detach=True,
        ports=None,
        privileged=False,
        auto_remove=False,
        hostname="js-ng",
    ):
        """Creates a docker container without starting it

        Args:
            name (str): name of the docker container
            image (str): image of the docker container
            command (str or list) – The command to run in the container.
            environment (dict or list) – Environment variables to set inside the container, as a dictionary or a list of strings in the format ["SOMEVARIABLE=xxx"].
            entrypoint (str or list) – The entrypoint for the container.
            volumes (dict or list) –
                A dictionary to configure volumes mounted inside the container. The key is either the host path or a volume name, and the value is a dictionary with the keys:
                bind The path to mount the volume inside the container
                mode Either rw to mount the volume read/write, or ro to mount it read-only.
                example
                {'/home/user1/': {'bind': '/mnt/vol2', 'mode': 'rw'},
                '/var/www': {'bind': '/mnt/vol1', 'mode': 'ro'}}
            devices (list) –
                Expose host devices to the container, as a list of strings in the form <path_on_host>:<path_in_container>:<cgroup_permissions>.
                For example, /dev/sda:/dev/xvda:rwm allows the container to have read-write access to the host’s /dev/sda via a node named /dev/xvda inside the container.
            detach (bool, optional): detach from container after running it.
            ports The port number, as an integer. For example,
                - {'2222/tcp': 3333} will expose port 2222 inside the container as port 3333 on the host.
                - None, to assign a random host port. For example, {'2222/tcp': None}.
                - A tuple of (address, port) if you want to specify the host interface. For example, {'1111/tcp': ('127.0.0.1', 1111)}.
                - A list of integers, if you want to bind multiple host ports to a single container port. For example, {'1111/tcp': [1234, 4567]}.
            privileged (bool) – Give extended privileges to this container.
            auto_remove (bool) – enable auto-removal of the container on daemon side
            hostname (str) - hostname to be set on docker container default "js-ng"
        Returns:
            container: container object
        """
        docker = self.client.containers.create(
            name=name,
            image=image,
            command=command,
            environment=environment,
            entrypoint=entrypoint,
            volumes=volumes,
            devices=devices,
            detach=detach,
            ports=ports,
            privileged=privileged,
            auto_remove=auto_remove,
            hostname=hostname,
        )
        return docker

    def run(
        self,
        name,
        image,
        command=None,
        environment=None,
        entrypoint=None,
        volumes=None,
        devices=None,
        detach=True,
        ports=None,
        privileged=False,
        auto_remove=False,
        hostname="js-ng",
    ):
        """Runs docker container
        Args:
            name (str): name of the docker container
            image (str): image of the docker container
            command (str or list) – The command to run in the container.
            environment (dict or list) – Environment variables to set inside the container, as a dictionary or a list of strings in the format ["SOMEVARIABLE=xxx"].
            entrypoint (str or list) – The entrypoint for the container.
            volumes (dict or list) –
                A dictionary to configure volumes mounted inside the container. The key is either the host path or a volume name, and the value is a dictionary with the keys:
                bind The path to mount the volume inside the container
                mode Either rw to mount the volume read/write, or ro to mount it read-only.
                example
                {'/home/user1/': {'bind': '/mnt/vol2', 'mode': 'rw'},
                '/var/www': {'bind': '/mnt/vol1', 'mode': 'ro'}}
            devices (list) –
                Expose host devices to the container, as a list of strings in the form <path_on_host>:<path_in_container>:<cgroup_permissions>.
                For example, /dev/sda:/dev/xvda:rwm allows the container to have read-write access to the host’s /dev/sda via a node named /dev/xvda inside the container.
            detach (bool, optional): detach from container after running it.
            ports The port number, as an integer. For example,
                - {'2222/tcp': 3333} will expose port 2222 inside the container as port 3333 on the host.
                - None, to assign a random host port. For example, {'2222/tcp': None}.
                - A tuple of (address, port) if you want to specify the host interface. For example, {'1111/tcp': ('127.0.0.1', 1111)}.
                - A list of integers, if you want to bind multiple host ports to a single container port. For example, {'1111/tcp': [1234, 4567]}.
            privileged (bool) – Give extended privileges to this container.
            auto_remove (bool) – enable auto-removal of the container on daemon side
            hostname (str) - hostname to be set on docker container default "js-ng"
        Returns:
            container: container object
        """
        docker = self.client.containers.run(
            name=name,
            image=image,
            command=command,
            environment=environment,
            entrypoint=entrypoint,
            volumes=volumes,
            devices=devices,
            detach=detach,
            ports=ports,
            privileged=privileged,
            auto_remove=auto_remove,
            hostname=hostname,
        )
        return docker

    def get(self, container_id):
        """Runs docker container
        Args:
            container_id (str): Id or name of the docker container

        Returns:
            container: container object
        """
        container = self.client.containers.get(container_id)
        return container

    def exists(self, container_id):
        try:
            self.client.containers.get(container_id)
            return True
        except docker.errors.NotFound:
            return False

    def delete(self, container_id, force=False):
        """Deletes docker container
        Args:
            container_id (str): Id or name of the docker container
            force (bool): image of the docker container

        Returns:
            bool: True container deleted
        """
        container = self.get(container_id)
        container.remove(force=force)
        return True

    def kill(self, container_id, sig=None):
        """Kills docker container
        Args:
            container_id (str): Id or name of the docker container
            sig (str or int): kill siganle, default SIGKILL

        Returns:
            bool: True container killed
        """
        container = self.get(container_id)
        container.kill(sig)
        return True

    def restart(self, container_id, timeout=10):
        """Kills docker container
        Args:
            container_id (str): Id or name of the docker container
            timeout (int): timeout to stop container before trying to kill

        Returns:
            bool: True if container restarted
        """
        container = self.get(container_id)
        container.restart(timeout=timeout)
        return True

    def start(self, container_id):
        """starts docker container
        Args:
            container_id (str): Id or name of the docker container
            timeout (int): timeout to stop container before trying to kill

        Returns:
            bool: True if container started
        """
        container = self.get(container_id)
        container.start()
        return True

    def stop(self, container_id):
        """stops docker container
        Args:
            container_id (str): Id or name of the docker container
            timeout (int): timeout to stop container before trying to kill

        Returns:
            bool: True if container started
        """
        container = self.get(container_id)
        container.stop()
        return True

    def list(self, all=False):
        """Returns list of docker containers created
        Args:
            all (bool): list all containers including stopped ones

        Returns:
            list: list of containers
        """
        return self.client.containers.list(all=all)

    def exec(
        self,
        container_id,
        cmd,
        stdout=True,
        stderr=True,
        stdin=False,
        tty=False,
        privileged=False,
        user="",
        detach=False,
        stream=False,
        socket=False,
        environment=None,
        workdir=None,
        demux=True,
    ):
        """Executes command docker container
        Args:
            container_id (str): Id or name of the docker container
            cmd (str or list) – Command to be executed
            stdout (bool) – Attach to stdout. Default: True
            stderr (bool) – Attach to stderr. Default: True
            stdin (bool) – Attach to stdin. Default: False
            tty (bool) – Allocate a pseudo-TTY. Default: False
            privileged (bool) – Run as privileged.
            user (str) – User to execute command as. Default: root
            detach (bool) – If true, detach from the exec command. Default: False
            stream (bool) – Stream response data. Default: False
            socket (bool) – Return the connection socket to allow custom read/write operations. Default: False
            environment (dict or list) – A dictionary or a list of strings in the following format ["PASSWORD=xxx"] or {"PASSWORD": "xxx"}.
            workdir (str) – Path to working directory for this exec session
            demux (bool) – Return stdout and stderr separately

        Returns:
            A tuple of (exit_code, output)
            exit_code: (int):
            Exit code for the executed command or None if either stream or socket is True.

            output: (generator, bytes, or tuple):
                If stream=True, a generator yielding response chunks.
                If socket=True, a socket object for the connection.
                If demux=True, a tuple of two bytes: stdout and stderr.
                A bytestring containing response data otherwise.
        """
        docker = self.get(container_id)
        return docker.exec_run(
            cmd=cmd,
            stdout=stdout,
            stderr=stderr,
            stdin=stdin,
            tty=tty,
            privileged=privileged,
            user=user,
            detach=detach,
            stream=stream,
            socket=socket,
            environment=environment,
            workdir=workdir,
            demux=demux,
        )
