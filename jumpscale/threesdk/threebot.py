import binascii
import os

import requests

from jumpscale.core.config import get_current_version
from jumpscale.core.exceptions import Value
from jumpscale.data.encryption import mnemonic
from jumpscale.data.encryption.exceptions import FailedChecksumError
from jumpscale.data.nacl.jsnacl import NACL
from jumpscale.god import j
from jumpscale.tools.console import ask_choice, ask_string, ask_yes_no, printcolors

from . import settings
from .container import Container

DEFAULT_CONTAINER_NAME = "3bot-ng"
DEFAULT_IMAGE = "threefoldtech/js-ng"
PERSISTENT_STORE = os.path.expanduser("~/.config/jumpscale/containers")


NETWORKS = {"mainnet": "explorer.grid.tf", "testnet": "explorer.testnet.grid.tf", "devnet": "explorer.devnet.grid.tf"}


class IdentityManager:
    def __init__(self, identity: str = "", email: str = None, words: str = None, explorer: str = None):
        self.identity = identity
        self.email = email
        self.words = words
        self.explorer = explorer

    def reset(self):
        self.identity = ""
        self.email = ""
        self.words = ""
        self.explorer = ""

    def _check_keys(self, user_explorer_key, user_app):
        if not user_app:
            return True
        pub_key_app = j.data.serializers.base64.decode(user_app["publicKey"])
        if binascii.unhexlify(user_explorer_key) != pub_key_app:
            return False
        return True

    def _get_user(self):
        response = requests.get(f"https://login.threefold.me/api/users/{self.identity}")
        if response.status_code == 404:
            raise j.core.exceptions.Value(
                "\nThis identity does not exist in 3bot mobile app connect, Please create an idenity first using 3Bot Connect mobile Application\n"
            )
        userdata = response.json()

        resp = requests.get("https://{}/explorer/users".format(self.explorer), params={"name": self.identity})
        if resp.status_code == 404 or resp.json() == []:
            return None, userdata
        else:
            users = resp.json()

            if not self._check_keys(users[0]["pubkey"], userdata):
                raise j.core.exceptions.Value(
                    f"\nYour 3bot on {self.explorer} seems to have been previously registered with a different public key.\n"
                    "Please contact support.grid.tf to reset it.\n"
                    "Note: use the same email registered on the explorer to contact support otherwise we cannot reset the account.\n"
                )

            if users:
                return (users[0], userdata)
            return None, userdata

    def _check_email(self, email):
        resp = requests.get("https://{}/explorer/users".format(self.explorer), params={"email": email})
        users = resp.json()
        if users:
            return True
        return False

    def ask_identity(self, identity=None, explorer=None):
        def _fill_identity_args(identity, explorer):
            def fill_words():
                words = ask_string("Copy the phrase from your 3bot Connect app here.")
                self.words = words

            def fill_identity():
                identity = ask_string("what is your threebot name (identity)?")
                if "." not in identity:
                    identity += ".3bot"
                self.identity = identity

            if identity:
                if self.identity != identity and self.identity:
                    self.reset()
                self.identity = identity

            if explorer:
                self.explorer = explorer
            elif not self.explorer:
                response = ask_choice(
                    "Which network would you like to register to? ", ["mainnet", "testnet", "devnet", "none"]
                )
                self.explorer = NETWORKS.get(response, None)
            if not self.explorer:
                return True

            user, user_app = None, None
            while not user:
                fill_identity()
                try:
                    user, user_app = self._get_user()
                except j.core.exceptions.Value as e:
                    response = ask_choice(f"{e}. What would you like to do?", ["restart", "reenter"],)
                    if response == "restart":
                        return False

            while not self.email:
                self.email = ask_string("What is the email address associated with your identity?")
                if self._check_email(self.email):
                    break
                else:
                    self.email = None
                    response = ask_choice(
                        "This email is currently associated with another identity. What would you like to do?",
                        ["restart", "reenter"],
                    )
                    if response == "restart":
                        return False

            print("Configured email for this identity is {}".format(self.email))

            # time to do validation of words
            hexkey = None
            while True:
                if not self.words:
                    fill_words()
                try:
                    seed = mnemonic.mnemonic_to_key(self.words.strip())
                    hexkey = NACL(seed).get_verify_key_hex()
                    if (user and hexkey != user["pubkey"]) or not self._check_keys(hexkey, user_app):
                        raise Exception
                    else:
                        return True
                except Exception:
                    choice = ask_choice(
                        "\nSeems one or more more words entered is invalid.\nWhat would you like to do?\n",
                        ["restart", "reenter"],
                    )
                    if choice == "restart":
                        return False

                if hexkey != user["pubkey"]:
                    choice = ask_choice(
                        f"\nUser with name: {identity} not registered with entered phrase.\nWhat would you like to do?\n",
                        ["restart", "reenter"],
                    )
                    if choice == "restart":
                        return False

        while True:
            if _fill_identity_args(identity, explorer):
                return self.identity, self.email, self.words, self.explorer


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
            identity_data = IdentityManager(identity, email, words, explorer)
            identity, email, words, explorer = identity_data.ask_identity()

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
