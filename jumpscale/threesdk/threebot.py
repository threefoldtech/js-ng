import os


from jumpscale.core.config import get_current_version
from jumpscale.core.exceptions import Value

from . import settings
from .container import Container
from .identitymanager import IdentityManager

DEFAULT_CONTAINER_NAME = "3bot-ng"
DEFAULT_IMAGE = "threefoldtech/js-ng"
PERSISTENT_STORE = os.path.expanduser("~/.config/jumpscale/containers")


class ThreeBot(Container):
    """
    Manage your threebot
    """

    @staticmethod
    def install(
        name=None, image=None, identity=None, email=None, words=None, explorer=None, development: bool = None,
    ):
        """Creates a threebot container

        Args:
            name (str, optional): name of the container. Defaults to 3bot-ng
            image (str, optional): container image. Defaults to "threefoldtech/js-ng:latest".
            identity (str, optional): threebot name. Defaults to None.
            email (str, optional): threebot email. Defaults to None.
            words (str, optional): seed phrase of the user. Defaults to None.
            explorer (str, optional): which explorer network to use: mainnet, testnet, devnet. Defaults to None.
            development (bool, optional): if true will mount codedir. Defaults to False.

        Raises:
            Value: Container with specified name already exists
            Value: explorer not in mainnet, testnet, devnet
        """
        if development is None:
            development = settings.expert
        name = name or DEFAULT_CONTAINER_NAME
        current_version = get_current_version()
        image = image or f"{DEFAULT_IMAGE}:{current_version}"

        pers_path = f"{PERSISTENT_STORE}/{name}"
        configure = not os.path.exists(pers_path)
        if configure:
            identity = IdentityManager(identity, email, words, explorer)
            identity, email, words, explorer = identity.ask_identity()

        os.makedirs(PERSISTENT_STORE, exist_ok=True)
        volumes = {pers_path: {"bind": "/root/.config/jumpscale", "mode": "rw"}}

        container = Container.install(name, image, development, volumes)
        container.exec_run(["redis-server", "--daemonize yes"])

        if configure:
            container.exec_run(["jsng", f"j.core.identity.new('default', '{identity}', '{email}', '{words}')"])
            container.exec_run(["jsng", "j.core.identity.set_default('default')"])

    @staticmethod
    def jsng(name=DEFAULT_CONTAINER_NAME):
        """Get's shell in threebot

        Args:
            name (str): name of the container
        """
        Container.exec(name, "jsng")

    @staticmethod
    def shell(name=DEFAULT_CONTAINER_NAME):
        """Get's shell in threebot

        Args:
            name (str): name of the container
        """
        Container.exec(name, "bash")
