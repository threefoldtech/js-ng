import sys

from jumpscale.loader import j


class Application:
    def __init__(self):
        sys.excepthook = j.tools.errorhandler.excepthook

    @property
    def process_id(self):
        return j.sals.process.get_my_process().pid
