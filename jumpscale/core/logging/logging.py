import math
import loguru
import msgpack
import json

from abc import ABC, abstractmethod

from jumpscale.loader import j


LEVELS = {
    10: "DEBUG",
    20: "INFO",
    30: "WARNING",
    40: "ERROR",
    50: "CRITICAL",
}


class LogHandler(ABC):
    """the interface every cutom log handler should implement"""

    @abstractmethod
    def _handle(self, message, **kwargs):
        pass


class Logger:
    def __init__(self, appname: str = "init"):
        """Logger init method
        """
        self._logger = loguru.logger.bind(appname=appname)
        self._appname = appname

    @property
    def appname(self):
        return self._appname

    def set_appname(self, appname):
        self._appname = appname
        self._logger = self._logger.bind(appname=appname)

    def add_handler(self, *args, **kwargs):
        """Add handler to the logger
        takes the same parameters of loguru.logger.add
        """
        self._logger.add(*args, **kwargs)

    def add_custom_handler(self, name: str, handler: LogHandler, *args, **kwargs):
        """Add custom log handler

        Arguments:
            handler {LogHandler} -- handler function
        """
        setattr(self, name, handler)
        self._logger.add(handler._handle, **kwargs)

    def _log(self, level, message, *args, category, data, exception=None):
        self._logger.opt(depth=2, exception=exception).bind(category=category, data=data).log(level, message, *args)

    def debug(self, message, *args, category: str = "", data: dict = None):
        """Log debug message
        """
        self._log("DEBUG", message, *args, category=category, data=data)

    def info(self, message, *args, category: str = "", data: dict = None):
        """Log info message
        """
        self._log("INFO", message, *args, category=category, data=data)

    def warning(self, message, *args, category: str = "", data: dict = None):
        """Log warning message
        """
        self._log("WARNING", message, *args, category=category, data=data)

    def error(self, message, *args, category: str = "", data: dict = None):
        """Log error message
        """
        self._log("ERROR", message, *args, category=category, data=data)

    def critical(self, message, *args, category: str = "", data: dict = None):
        """Log critical message
        """
        self._log("CRITICAL", message, *args, category=category, data=data)

    def exception(
        self, message, *args, category: str = "", data: dict = None, level: int = 40, exception: Exception = None
    ):
        """Log exception message
        """
        self._log(LEVELS.get(level, 40), message, *args, category=category, data=data, exception=exception)


class RedisLogHandler(LogHandler):
    def __init__(self, max_size: int = 1000, dump: bool = True, dump_dir: str = None):
        self._max_size = max_size
        self._dump = dump
        self._dump_dir = dump_dir or "/tmp"
        self._rkey = "logs:%s:records"
        self._rkey_incr = "logs:%s:incr"
        self.__db = None

        if self._dump_dir:
            j.sals.fs.mkdirs(self._dump_dir)

    @property
    def _appname(self):
        return j.core.application.appname

    @property
    def _db(self):
        if self.__db is None:
            self.__db = j.core.db
        return self.__db

    @property
    def max_size(self):
        return self._max_size

    @property
    def dump(self):
        return self._dump

    @property
    def dump_dir(self):
        return self._dump_dir

    def _map_identifier(self, identifier):
        part = math.ceil(identifier / self.max_size) * self.max_size
        index = (identifier % self.max_size) - 1
        return part, index

    def _dump_records(self, appname, path):
        j.sals.fs.mkdir(j.sals.fs.parent(path))
        records = self._db.lrange(self._rkey % appname, 0, self.max_size - 1)
        j.sals.fs.write_bytes(path, msgpack.dumps(records))

    def _process_message(self, message):
        record = json.loads(message)["record"]
        appname = record["extra"]["appname"]
        record_id = self._db.incr(self._rkey_incr % appname)
        return dict(
            id=record_id,
            appname=appname,
            message=record["message"],
            level=record["level"]["no"],
            linenr=record["line"],
            file=record["file"],
            processid=record["process"]["id"],
            context=record["function"],
            epoch=record["time"]["timestamp"],
            exception=record["exception"],
            category=record["extra"].get("category", ""),
            data=record["extra"].get("data", {}),
        )

    def _clean_up(self, appname):
        self._db.ltrim(self._rkey % appname, self.max_size, -1)

    def _handle(self, message: str, **kwargs):
        """Logging handler

        Arguments:
            message {str} -- message string
        """
        if not self._db.is_running():
            return

        record = self._process_message(message)
        appname = record["appname"]

        rkey = self._rkey % appname
        self._db.rpush(rkey, json.dumps(record))

        if self._db.llen(rkey) > self.max_size:
            if self.dump:
                part, _ = self._map_identifier(record["id"] - 1)
                path = j.sals.fs.join_paths(self.dump_dir, appname, "%s.msgpack" % part)
                self._dump_records(appname, path)

            self._clean_up(appname)

    def records_count(self, appname: str = "init") -> int:
        """Gets total number of the records of the app

        Arguments:
            appname {str} -- app name

        Returns:
            init -- total number of the records
        """
        count = self._db.get(self._rkey_incr % appname)
        if count:
            return int(count)
        return 0

    def record_get(self, identifier: int, appname: str = "init") -> dict:
        """Get app log record by its identifier

        Arguments:
            identifier {int} -- record identifier
            appname {str} -- app name

        Returns:
            dict -- requested log record
        """
        count = self.records_count(appname)
        part, index = self._map_identifier(identifier)

        if identifier > count:
            return

        if part > count - self.max_size:
            record = self._db.lindex(self._rkey % appname, index)
            return json.loads(record)

        if self.dump:
            path = j.sals.fs.join_paths(self.dump_dir, appname, "%s.msgpack" % part)
            if j.sals.fs.exists(path):
                records = msgpack.loads(j.sals.fs.read_bytes(path))
                if records and len(records) > index:
                    return json.loads(records[index])

    def remove_all_records(self, appname: str):
        """Delete all app's log records

        Arguments:
            appname {str} -- app name
        """
        self._db.delete(self._rkey % appname, self._rkey_incr % appname)
        path = j.sals.fs.join_paths(self.dump_dir, appname)

        if self.dump:
            j.sals.fs.rmtree(path)

    def tail(self, appname: str = "init", limit: int = None) -> iter:
        """Tail records

        Keyword Arguments:
            appname (str) -- appname (default: {""})
            limit (int) -- max number of record to be returned (default: {None})

        Yields:
            iter -- iterator of the requested logs
        """
        if limit:
            limit = limit - 1

        records = self._db.lrange(self._rkey % appname, 0, limit or -1)
        for record in records:
            yield json.loads(record)
