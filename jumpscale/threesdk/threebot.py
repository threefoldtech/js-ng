import requests
import os

from .container import Container
from . import settings

from jumpscale.core.exceptions import Value
from jumpscale.data.encryption import mnemonic
from jumpscale.data.encryption.exceptions import FailedChecksumError
from jumpscale.data.nacl.jsnacl import NACL
from jumpscale.tools.console import ask_string, ask_choice, printcolors, ask_yes_no
from jumpscale.core.config import get_current_version

DEFAULT_CONTAINER_NAME = "3bot-ng"
DEFAULT_IMAGE = "threefoldtech/js-ng"
PERSISTENT_STORE = os.path.expanduser("~/.config/jumpscale/containers")


NETWORKS = {"mainnet": "explorer.grid.tf", "testnet": "explorer.testnet.grid.tf", "devnet": "explorer.devnet.grid.tf"}


def check_identity(identity, email, words, explorer):
    res = requests.get(f"https://{NETWORKS[explorer]}/explorer/users", params={"name": identity, "email": email}).json()
    if not res:
        return f"Couldn't find user with name: {identity} and email: {email} in explorer network: {explorer}"
    user = res[0]
    try:
        seed = mnemonic.mnemonic_to_key(words.strip())
        verify_key_hex = NACL(seed).get_verify_key_hex()
    except FailedChecksumError:
        return "Phrase words entered are not valid"

    if verify_key_hex != user["pubkey"]:
        return f"User with name: {identity} not registered with entered phrase"


def ensure_identity(identity, email, words, explorer):

    identity_data = ()
    while True:
        _identity = identity or ask_string("Please enter your threebot name(i,e name.3bot): ")
        _email = email or ask_string("Please enter your threebot email: ")
        _words = words or ask_string("Please enter your threebot phrase: ")
        _explorer = explorer or ask_choice("Please choose your explorer network: ", list(NETWORKS))

        error_message = check_identity(_identity, _email, _words, _explorer)
        if error_message:
            printcolors("{RED}Verifying identity data failed, error was: {RESET}" + error_message)
            if ask_yes_no("Do you want to reenter the values? ([y,n])\n") == "y":
                continue
        else:
            identity_data = (_identity, _email, _words, _explorer)
        break
    return identity_data


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
        if explorer and explorer not in NETWORKS:
            raise Value(f"allowed explorer values are {','.join(NETWORKS)}")

        pers_path = f"{PERSISTENT_STORE}/{name}"
        configure = not os.path.exists(pers_path)
        if configure:
            identity_data = ensure_identity(identity, email, words, explorer)
            if not identity_data:
                raise Value("Installation aborted, please enter correct identity information")
            identity, email, words, explorer = identity_data

        os.makedirs(PERSISTENT_STORE, exist_ok=True)
        volumes = {pers_path: {"bind": "/root/.config/jumpscale", "mode": "rw"}}
        container = Container.install(name, image, development, volumes)

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
