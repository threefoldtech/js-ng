from jumpscale.loader import j
import sys

DEFAULT_APP_NAME = "init"


class Application:
    def __init__(self):
        self.appname = DEFAULT_APP_NAME
        sys.excepthook = j.tools.errorhandler.excepthook

    @property
    def process_id(self):
        return j.sals.process.get_my_process().pid

    def start(self, appname):
        j.logger.add_appname(appname)

        if j.core.db.is_running():
            j.core.db.sadd("applications", appname)

        j.logger.info("Application {} is started, process id: {}", appname, self.process_id)

    def stop(self, appname):
        j.logger.info("Application {} is stopped", appname)

        if j.core.db.is_running():
            j.core.db.srem("applications", appname)
