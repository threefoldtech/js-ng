import os


class Dirs:

    HOMEDIR = os.path.expanduser("~")
    BASEDIR = os.path.join(HOMEDIR, "sandbox")
    BINDIR = os.path.join(BASEDIR, "bin")
    CFGDIR = os.path.join(BASEDIR, "cfg")
    CODEDIR = os.path.join(BASEDIR, "code")
    VARDIR = os.path.join(BASEDIR, "var")
    LOGDIR = os.path.join(VARDIR, "log")
    TEMPLATEDIR = os.path.join(VARDIR, "templates")
    TMPDIR = "/tmp/jumpscale"
