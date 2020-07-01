from gevent import monkey

monkey.patch_all(subprocess=False)  # noqa: E402
import click
import os
import pathlib
import sys

from jumpscale.loader import j  # noqa:
from jumpscale.core.config.config import get_config

BASE_CONFIG_DIR = os.path.join(os.environ.get("HOME", "/root"), ".jsng")
HISTORY_FILENAME = os.path.join(BASE_CONFIG_DIR, "history.txt")


@click.command()
@click.argument("command", required=False)
def run(command):
    """Executes the passed command and initiates a jsng shell if no command is passed."""
    os.makedirs(BASE_CONFIG_DIR, exist_ok=True)
    pathlib.Path(HISTORY_FILENAME).touch()
    if command is None:
        config = get_config()
        if config["shell"] == "ipython":
            from IPython import embed
            sys.exit(embed(colors="neutral"))
        else:
            from jumpscale.shell import ptconfig
            from ptpython.repl import embed
            sys.exit(embed(globals(), locals(), configure=ptconfig, history_filename=HISTORY_FILENAME))
    else:
        sys.exit(print(eval(command)))
