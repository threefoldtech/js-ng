import math
import loguru
import msgpack
import json

from abc import ABC, abstractmethod

from loguru._get_frame import get_frame

from jumpscale.core.exceptions import Value
from jumpscale.loader import j


LEVELS = {
    10: "DEBUG",
    20: "INFO",
    30: "WARNING",
    40: "ERROR",
    50: "CRITICAL",
}

# init is kept as a name for backward compatibility
DEFAULT_APP_NAME = "init"


class LogHandler(ABC):
    """the interface every cutom log handler should implement"""

    @abstractmethod
    def _handle(self, message, **kwargs):
        pass


class Logger:
    def __init__(self):
        self._default_app_name = DEFAULT_APP_NAME
        self._logger = loguru.logger.bind(app_name=self._default_app_name)

    @property
    def default_app_name(self):
        return self._default_app_name

    def add_handler(self, *args, **kwargs):
        """
        Add handler to the logger

        takes the same parameters of loguru.logger.add
        """
        return self._logger.add(*args, **kwargs)

    def add_custom_handler(self, name: str, handler: LogHandler, *args, **kwargs):
        """
        Add custom log handler

        Arguments:
            handler (LogHandler): handler function
        """
        setattr(self, name, handler)
        return self._logger.add(handler._handle, **kwargs)

    def remove_handler(self, handler_id: int):
        """
        Remove loguru handler by id

        The pre-configured handler has the id of `0`

        Args:
            handler_id (int): handler id that was returned by `add_handler` method
        """
        self._logger.remove(handler_id)

    def _log(self, level, message, *args, category, data, exception=None):
        self._logger.opt(depth=2, exception=exception).bind(category=category, data=data).log(level, message, *args)

    def debug(self, message, *args, category: str = "", data: dict = None):
        """Log debug message"""
        self._log("DEBUG", message, *args, category=category, data=data)

    def info(self, message, *args, category: str = "", data: dict = None):
        """Log info message"""
        self._log("INFO", message, *args, category=category, data=data)

    def warning(self, message, *args, category: str = "", data: dict = None):
        """Log warning message"""
        self._log("WARNING", message, *args, category=category, data=data)

    def error(self, message, *args, category: str = "", data: dict = None):
        """Log error message"""
        self._log("ERROR", message, *args, category=category, data=data)

    def critical(self, message, *args, category: str = "", data: dict = None):
        """Log critical message"""
        self._log("CRITICAL", message, *args, category=category, data=data)

    def exception(
        self, message, *args, category: str = "", data: dict = None, level: int = 40, exception: Exception = None
    ):
        """Log exception message"""
        self._log(LEVELS.get(level, 40), message, *args, category=category, data=data, exception=exception)


class MainLogger(Logger):
    def __init__(self):
        super().__init__()

        # mapping between module -> app_name
        self._module_apps = {}
        self._apps_rkey = "applications"
        # patch the logger to update app name per module
        self._logger = self._logger.patch(self._update_app_name)

    def _get_caller_module(self):
        # from loguru/_logger.py
        frame = get_frame(2)

        try:
            module_name = frame.f_globals["__name__"]
        except KeyError:
            module_name = None

        return module_name

    def _add_app(self, app_name):
        if j.core.db.is_running():
            j.core.db.sadd(self._apps_rkey, app_name)

    def _remove_app(self, app_name):
        if j.core.db.is_running():
            j.core.db.srem(self._apps_rkey, app_name)

    def register(self, app_name, module_name=None):
        """
        Register and bind given module (and sub-modules) logs with a given app name

        Will also add the app to `applications` set in redis.

        If `module_name` is not passed or empty, it would be the caller module name.

        Args:
            app_name (str): app name
            module_name (str, optional): module name. Defaults to None.
        """
        if not app_name:
            raise Value(f"invalid app name '{app_name}'")

        if not module_name:
            module_name = self._get_caller_module()

        self._module_apps[module_name] = app_name
        self._add_app(app_name)

        self.info(f"Logging from '{module_name}' is now bound to '{app_name}' app")

    def unregister(self, module_name=None):
        """
        Unregister a module from log binding with the app name.

        Will also remove the app from `applications` set in redis.

        If `module_name` is not passed or empty, it would be the caller module name.

        Args:
            module_name (str, optional): module name. Defaults to None.
        """
        if not module_name:
            module_name = self._get_caller_module()

        if module_name in self._module_apps:
            app_name = self._module_apps[module_name]
            del self._module_apps[module_name]
            self._remove_app(app_name)
            self.info(f"Logging from '{module_name}' is now unbound to '{app_name}' app")

    def get_app_names(self):
        """
        Get a set of all registered app names

        If redis is running, it would get them from `applications` set.

        Returns:
            set: available app names
        """
        apps = {DEFAULT_APP_NAME}

        if not j.core.db.is_running():
            apps.update(self._module_apps.values())
        else:
            apps.update([app.decode() for app in j.core.db.smembers("applications")])

        return apps

    def _get_app_name(self, module, sub_module=None):
        """Get app name for a given module

        Args:
            module (str): module name (e.g. jumpscale.servers.gedis)
            sub_module (str, optional): will match the same app name if given (e.g. jumpscale.servers.gedis.helpers). Defaults to None.

        Returns:
            str: app name
        """
        if module in self._module_apps:
            value = self._module_apps[module]

            # add sub-module if provided too for faster search
            if sub_module and sub_module != module:
                self._module_apps[sub_module] = value

            return value

        # go up 1 level
        new_module, _, _ = module.rpartition(".")
        # no parent_module, cannot go up anymore
        if not new_module:
            return ""

        # do the search again
        return self._get_app_name(new_module, module)

    def _update_app_name(self, record):
        """
        Update app_name in record["extra"] if found in module -> app_name mapping

        Args:
            record (dict): loguru record
        """
        app_name = self._get_app_name(record["name"])
        if app_name:
            record["extra"]["app_name"] = app_name


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

    def _dump_records(self, app_name, path):
        j.sals.fs.mkdir(j.sals.fs.parent(path))
        records = self._db.lrange(self._rkey % app_name, 0, self.max_size - 1)
        j.sals.fs.write_bytes(path, msgpack.dumps(records))

    def _process_message(self, message):
        record = json.loads(message)["record"]
        app_name = record["extra"]["app_name"]
        record_id = self._db.incr(self._rkey_incr % app_name)
        return dict(
            id=record_id,
            app_name=app_name,
            module=record["name"],
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

    def _clean_up(self, app_name):
        self._db.ltrim(self._rkey % app_name, self.max_size, -1)

    def _handle(self, message: str, **kwargs):
        """Logging handler

        Arguments:
            message {str} -- message string
        """
        if not self._db.is_running():
            return

        record = self._process_message(message)
        app_name = record["app_name"]

        rkey = self._rkey % app_name
        self._db.rpush(rkey, json.dumps(record))

        if self._db.llen(rkey) > self.max_size:
            if self.dump:
                part, _ = self._map_identifier(record["id"] - 1)
                path = j.sals.fs.join_paths(self.dump_dir, app_name, "%s.msgpack" % part)
                self._dump_records(app_name, path)

            self._clean_up(app_name)

    def records_count(self, app_name: str = DEFAULT_APP_NAME) -> int:
        """Gets total number of the records of the app

        Arguments:
            app_name (str): app name

        Returns:
            init -- total number of the records
        """
        count = self._db.get(self._rkey_incr % app_name)
        if count:
            return int(count)
        return 0

    def record_get(self, identifier: int, app_name: str = DEFAULT_APP_NAME) -> dict:
        """Get app log record by its identifier

        Arguments:
            identifier {int} -- record identifier
            app_name {str} -- app name

        Returns:
            dict: requested log record
        """
        count = self.records_count(app_name)
        part, index = self._map_identifier(identifier)

        if identifier > count:
            return

        if part > count - self.max_size:
            record = self._db.lindex(self._rkey % app_name, index)
            return json.loads(record)

        if self.dump:
            path = j.sals.fs.join_paths(self.dump_dir, app_name, "%s.msgpack" % part)
            if j.sals.fs.exists(path):
                records = msgpack.loads(j.sals.fs.read_bytes(path))
                if records and len(records) > index:
                    return json.loads(records[index])

    def remove_all_records(self, app_name: str):
        """Delete all app's log records

        Arguments:
            app_name (str): app name
        """
        self._db.delete(self._rkey % app_name, self._rkey_incr % app_name)
        path = j.sals.fs.join_paths(self.dump_dir, app_name)

        if self.dump:
            j.sals.fs.rmtree(path)

    def tail(self, app_name: str = DEFAULT_APP_NAME, limit: int = None) -> iter:
        """Tail records

        Keyword Arguments:
            app_name (str): app name.
            limit (int, optional): max number of record to be returned per page (default: max size)

        Yields:
            iter: iterator of the requested logs
        """
        if limit:
            limit = limit - 1

        records = self._db.lrange(self._rkey % app_name, 0, limit or -1)
        for record in records:
            yield json.loads(record)
