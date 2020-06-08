from jumpscale.clients.docker.docker import DockerClient
from jumpscale.core.dirs.dirs import Dirs
from jumpscale.core.exceptions import Value

docker_client = DockerClient()


class Container:
    """Container management
    """

    @staticmethod
    def install(
        name, image="threefoldtech/js-ng:latest", ports=None, volumes=None, devices=None, expert=False,
    ):
        """Creates a container
        """
        volumes = volumes or {}
        if docker_client.exists(name):
            raise Value("Container with specified name already exists")

        if expert:
            volumes.update({Dirs.CODEDIR: {"bind": "/sandbox/code", "mode": "rw"}})

        docker_client.run(name, image, entrypoint="/sbin/my_init", ports=ports, volumes=volumes, devices=None)
