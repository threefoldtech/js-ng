from jumpscale.loader import j


def _get_identifier(appname, message, public_message, category, alert_type):
    return j.data.hash.md5(":".join([appname, message, public_message, category, alert_type]))


class Alert:
    def __init__(self):
        self.id = None
        self.type = None
        self.level = 0
        self.appname = None
        self.category = None
        self.message = None
        self.public_message = None
        self.count = 0
        self.status = None
        self.first_occurrence = None
        self.last_occurrence = None
        self.data = None
        self.event = []
        self.tracebacks = []

    @classmethod
    def loads(cls, value):
        json = j.data.serializers.json.loads(value)
        instance = cls()
        instance.__dict__ = json
        return instance

    @property
    def identifier(self):
        return _get_identifier(self.appname, self.message, self.public_message, self.category, self.type)

    @property
    def json(self):
        return self.__dict__

    def dumps(self):
        return j.data.serializers.json.dumps(self.__dict__)


class AlertsHandler:
    def __init__(self):
        self._rkey = "alerts"
        self._rkey_id = "alerts:id"
        self._rkey_incr = "alerts:id:incr"
        self._db = None

    def __dir__(self):
        return ("get", "find", "alert_raise", "count", "reset", "delete", "delete_all")

    @property
    def db(self):
        if self._db is None:
            self._db = j.core.db
        return self._db

    def get(self, alert_id: int = None, identifier: str = None, die: bool = True) -> Alert:
        """Get alert by its id or identifier

        Keyword Arguments:
            alert_id {int} -- alert id (default: {None})
            identifier {str} -- alert identifier (default: {None})
            die {bool} -- flag to rasie exception if alert is not found (default: {True})

        Raises:
            j.core.exceptions.NotFound: alert is not found
            j.core.exceptions.Value: invalid arguments

        Returns:
            Alert -- [description]
        """
        if not (alert_id or identifier):
            raise j.core.exceptions.Value("Either alert id or alert identifier are required")

        alert_id = alert_id or self.db.hget(self._rkey_id, identifier)
        if alert_id:
            alert = self.db.hget(self._rkey, alert_id)
            if alert:
                return Alert.loads(alert)
        if die:
            raise j.core.exceptions.NotFound("Requested alert is not found")

    def find(
        self,
        appname: str = "",
        category: str = "",
        message: str = "",
        pid: int = None,
        start_time: int = None,
        end_time: int = None,
    ) -> Alert:

        """Find alerts

        Keyword Arguments:
            appname {str} -- filter by allert app name (default: {""})
            category {str} -- filter by alert category (default: {""})
            message {str} -- filter by alert message (default: {""})
            pid {int} -- filter by process id (default: {None})
            start_time {int} -- filter by start time (default: {None})
            end_time {int} -- filter by end time (default: {None})

        Returns:
            Alert -- alert object
        """
        appname = appname.strip().lower()
        category = category.strip().lower()
        message = message.strip().lower()

        alerts = []
        items = self.db.hscan_iter(self._rkey)

        for item in items:
            alert = Alert.loads(item[1])

            if appname and appname != alert.appname:
                continue

            if category and category != alert.category:
                continue

            if message and (message not in alert.message and message not in alert.public_message):
                continue

            if start_time and start_time < alert.first_occurrence:
                continue

            if end_time and end_time > alert.last_occurrence:
                continue

            if pid:
                for traceback in alert.tracebacks:
                    if traceback["process_id"] == pid:
                        break
                else:
                    continue

            alerts.append(alert)
        return sorted(alerts, key=lambda alert: alert.id)

    def alert_raise(
        self,
        appname,
        message,
        public_message: str = "",
        category: str = "",
        alert_type: str = "event_system",
        level: int = 40,
        data: dict = None,
        timestamp: float = None,
        traceback: dict = None,
    ) -> Alert:

        """Raise a new alert

        Arguments:
            message {str} -- alert message

        Keyword Arguments:
            public_message {str} -- alert public message (default: {""})
            category {str} -- alert category (default: {""})
            alert_type {str} -- alert type (default: {"event_system"})
            level {int} -- alert level (default: {40})
            traceback {dict} -- alert traceback (default: {None})

        Returns:
            Alert -- alert object
        """
        if not self.db.is_running():
            return

        identifier = _get_identifier(appname, message, public_message, category, alert_type)
        alert = self.get(identifier=identifier, die=False) or Alert()

        if alert.id:
            if alert.status == "new":
                alert.status = "open"
            elif alert.status == "closed":
                alert.status = "reopened"
        else:
            alert.status = "new"
            alert.first_occurrence = timestamp or j.data.time.now().timestamp

        alert.appname = appname
        alert.category = category
        alert.message = message
        alert.public_message = public_message
        alert.level = level
        alert.type = alert_type
        alert.count += 1
        alert.last_occurrence = timestamp or j.data.time.now().timestamp

        if traceback:
            if len(alert.tracebacks) > 5:
                alert.tracebacks.pop(0)

        alert.tracebacks.append(traceback)
        self._save(alert)
        return alert

    def count(self) -> int:
        """Gets alerts count

        Returns:
            int -- total number of alerts
        """
        return self.db.hlen(self._rkey)

    def _save(self, alert: Alert):
        """Saves alert object in db

        Arguments:
            alert {Alert} -- alert object
        """
        if not alert.id:
            alert.id = self.db.incr(self._rkey_incr)

        self.db.hset(self._rkey, alert.id, alert.dumps())
        self.db.hset(self._rkey_id, alert.identifier, alert.id)

    def delete(self, alert_id: int = None, identifier: str = None):
        """Delete alert by its id or identifier

        Raises:
            j.core.exceptions.Value: invalid arguments

        Keyword Arguments:
            alert_id {int} -- alert id (default: {None})
            identifier {str} -- alert identifier (default: {None})
        """
        if not (alert_id or identifier):
            raise j.core.exceptions.Value("Either alert id or alert identifier are required")

        alert_id = alert_id or self.db.hget(self._rkey_id, identifier)
        if alert_id:
            self.db.hdel(self._rkey, alert_id)

    def delete_all(self):
        """Deletes all alerts
        """
        self.db.delete(self._rkey, self._rkey_id)

    def reset(self):
        """Delete all alerts and reset the db
        """
        self.delete_all()
        self.db.delete(self._rkey_incr)
