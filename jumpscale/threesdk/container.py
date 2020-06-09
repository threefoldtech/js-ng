from jumpscale.clients.docker.docker import DockerClient
from jumpscale.core.dirs.dirs import Dirs
from jumpscale.core.exceptions import Value

docker_client = DockerClient()


class Container:
    """Container management
    """

    @staticmethod
    def install(
        name, image, expert: bool = False,
    ):
        """Creates a container

        Args:
            name (str): name of the container
            image (str): container image.
            expert (bool, optional): if true will mount codedir. Defaults to False.

        Raises:
            Value: Container with specified name already exists
        """
        if docker_client.exists(name):
            raise Value("Container with specified name already exists")

        volumes = {}
        if expert:
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
    def stop(name):
        """Stops an existing container

        Args:
            name (str): name of the container
        """
        if not docker_client.exists(name):
            raise Value("Container with specified name doesn't exist")
        docker_client.stop(name)
