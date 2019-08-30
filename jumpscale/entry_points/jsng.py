import os
import pathlib
import sys

from jumpscale.god import j
from jumpscale.shell import ptconfig

from ptpython.repl import embed


BASE_CONFIG_DIR = os.path.join(os.environ["HOME"], ".jsng")
HISTORY_FILENAME = os.path.join(BASE_CONFIG_DIR, "history.txt")


def run():
    os.makedirs(BASE_CONFIG_DIR, exist_ok=True)
    pathlib.Path(HISTORY_FILENAME).touch()
    if len(sys.argv) == 1:
        sys.exit(embed(globals(), locals(), configure=ptconfig, history_filename=HISTORY_FILENAME))
    else:
        sys.exit(print(eval(sys.argv[1])))