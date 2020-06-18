from jumpscale.clients.docker.docker import DockerClient
from jumpscale.core.dirs.dirs import Dirs
from jumpscale.core.exceptions import Value
from jumpscale.core.executors.local import execute

docker_client = DockerClient()


class Container:
    """Container management
    """

    @staticmethod
    def install(name, image, development: bool = False, volumes=None):
        """Creates a container

        Args:
            name (str): name of the container
            image (str): container image.
            development (bool, optional): if true will mount codedir. Defaults to False.
            volumes (dict, optional): paths to be mounted

        Raises:
            Value: Container with specified name already exists
        """
        if docker_client.exists(name):
            raise Value("Container with specified name already exists")

        volumes = volumes or {}
        if development:
            volumes = {Dirs.CODEDIR: {"bind": "/sandbox/code", "mode": "rw"}}

        print(f"Creating container {name}")
        return docker_client.run(name, image, entrypoint="/sbin/my_init", volumes=volumes, detach=True)

    @staticmethod
    def start(name):
        """Starts an existing container

        Args:
            name (str): name of the container
        """
        if not docker_client.exists(name):
            raise Value("Container with specified name doesn't exist")
        docker_client.start(name)

    @staticmethod
    def exec(name, cmd):
        """Execute command in container

        Args:
            name (str): name of the container
            cmd (str or list): command to execute
        """
        basecmd = ["docker", "exec", "-it", name]
        if isinstance(cmd, str):
            basecmd.append(cmd)
        else:
            basecmd += cmd
        execute(basecmd, pty=True)

    @staticmethod
    def stop(name):
        """Stops an existing container

        Args:
            name (str): name of the container
        """
        if not docker_client.exists(name):
            raise Value("Container with specified name doesn't exist")
        docker_client.stop(name)

    @staticmethod
    def delete(name):
        Container.stop(name)
        docker_client.delete(name)
