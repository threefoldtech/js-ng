import requests
import nacl.encoding

from .container import Container

from jumpscale.core.exceptions import NotFound, Value
from jumpscale.data.encryption import mnemonic
from jumpscale.data.encryption.exceptions import FailedChecksumError
from jumpscale.data.nacl.jsnacl import NACL
from jumpscale.tools.console import ask_string, ask_choice, printcolors, ask_yes_no
from nacl.public import PrivateKey

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
        name="3bot-ng",
        image="threefoldtech/js-ng:latest",
        expert: bool = False,
        identity=None,
        email=None,
        words=None,
        explorer=None,
    ):
        """Creates a threebot container

        Args:
            name (str): name of the container
            image (str, optional): container image. Defaults to "threefoldtech/js-ng:latest".
            expert (bool, optional): if true will mount codedir. Defaults to False.
            identity (str, optional): threebot name. Defaults to None.
            email (str, optional): threebot email. Defaults to None.
            words (str, optional): seed phrase of the user. Defaults to None.
            explorer (str, optional): which explorer network to use: mainnet, testnet, devnet. Defaults to None.

        Raises:
            Value: Container with specified name already exists
            Value: explorer not in mainnet, testnet, devnet
        """
        if explorer and explorer not in NETWORKS:
            raise Value(f"allowed explorer values are {','.join(NETWORKS)}")

        identity, email, words, explorer = ensure_identity(identity, email, words, explorer)

        container = Container.install(name, image, expert)

        container.exec_run(["jsng", f"j.core.identity.new('default', '{identity}', '{email}', '{words}')"])
        container.exec_run(["jsng", "j.core.identity.set_default('default')"])
