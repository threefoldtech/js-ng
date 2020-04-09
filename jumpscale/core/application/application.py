from jumpscale.god import j

DEFAULT_APP_NAME = "init"


class Application:
    def __init__(self):
        self.appname = DEFAULT_APP_NAME

    @property
    def process_id(self):
        return j.sals.process.get_my_process().pid

    def start(self, appname):
        self.appname = appname
        j.core.logging.logger.info("Application {} is started, process id: {}", self.appname, self.process_id)

    def stop(self):
        j.core.logging.logger.info("Application {} is stopped", self.appname)
        self.appname = DEFAULT_APP_NAME
