from gevent import monkey

import click
import os
import pathlib
import sys

from jumpscale.core.config import get_config, get_current_version


BASE_CONFIG_DIR = os.path.join(os.environ.get("HOME", "/root"), ".jsng")
HISTORY_FILENAME = os.path.join(BASE_CONFIG_DIR, "history.txt")


@click.command()
@click.option("-p/-n", "--patch/--no-patch", default=True, help="Control gevent monkey patching")
@click.version_option(get_current_version())
@click.argument("command", required=False)
def run(command, patch):
    """Executes the passed command and initiates a jsng shell if no command is passed."""
    if patch:
        monkey.patch_all(subprocess=False)  # noqa: E402

    from jumpscale.loader import j  # noqa:

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
        sys.exit(print(exec(command)))
