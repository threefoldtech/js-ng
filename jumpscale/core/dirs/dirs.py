"""
This module defines main dirs in jumpscale to be used
"""

import os


class Dirs:

    HOMEDIR = os.path.expanduser("~")  # TODO: ؤاثؤن homedir defined in sal.fs
    BASEDIR = os.path.join(HOMEDIR, "sandbox")
    BINDIR = os.path.join(BASEDIR, "bin")
    CFGDIR = os.path.join(BASEDIR, "cfg")  # TODO: check conflict with core.config_root..
    CODEDIR = os.path.join(BASEDIR, "code")
    VARDIR = os.path.join(BASEDIR, "var")
    LOGDIR = os.path.join(VARDIR, "log")
    TEMPLATEDIR = os.path.join(VARDIR, "templates")
    TMPDIR = "/tmp/jumpscale"
