import math
import loguru
import msgpack

from abc import ABC, abstractmethod

from jumpscale.god import j


class CustomLogHandler(ABC):
    """the interface every cutom log handler should implement"""

    @abstractmethod
    def _handle(self, message, **kwargs):
        pass


class Logger:
    def __init__(self):
        """Logger init method
        """
        self.logger = loguru.logger

    def add_handler(self, *args, **kwargs):
        """Add handler to the logger
        takes the same parameters of loguru.logger.add
        """
        self.logger.add(*args, **kwargs)

    def add_custom_handler(self, name: str, handler: CustomLogHandler, *args, **kwargs):
        """Add custom log handler
        
        Arguments:
            handler {CustomLogHandler} -- handler function
        """
        setattr(self, name, handler)
        self.logger.add(handler._handle, **kwargs)


class RedisHandler(CustomLogHandler):
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

    def _dump_records(self, path):
        j.sals.fs.mkdir(j.sals.fs.parent(path))
        records = self._db.lrange(self._rkey % self._appname, 0, self.max_size - 1)
        j.sals.fs.write_bytes(path, msgpack.dumps(records))

    def _process_message(self, message):
        record = j.data.serializers.json.loads(message)["record"]
        appname = j.core.application.appname
        record_id = self._db.incr(self._rkey_incr % appname)
        return dict(
            id=record_id,
            appname=appname,
            name=record["name"],
            message=record["message"],
            level=record["level"]["no"],
            linenr=record["line"],
            processid=record["process"]["id"],
            context=record["function"],
            exception=record["exception"],
            epoch=record["time"]["timestamp"],
        )

    def _clean_up(self):
        self._db.ltrim(self._rkey % self._appname, self.max_size, -1)

    def _handle(self, message: str, **kwargs):
        """Logging handler
        
        Arguments:
            message {str} -- message string
        """
        if not self._db:
            return

        rkey = self._rkey % self._appname
        record = self._process_message(message)
        self._db.rpush(rkey, j.data.serializers.json.dumps(record))

        if self._db.llen(rkey) > self.max_size:
            if self.dump:
                part, _ = self._map_identifier(record["id"] - 1)
                path = j.sals.fs.join_paths(self.dump_dir, self._appname, "%s.msgpack" % part)
                self._dump_records(path)

            self._clean_up()

    def records_count(self, appname: str = "") -> int:
        """Gets total number of the records of the app
        
        Arguments:
            appname {str} -- app name
        
        Returns:
            init -- total number of the records
        """
        appname = appname or self._appname
        return int(self._db.get(self._rkey_incr % appname))

    def record_get(self, identifier: int, appname: str = "") -> dict:
        """Get app log record by its identifier
        
        Arguments:
            identifier {int} -- record identifier
            appname {str} -- app name
        
        Returns:
            dict -- requested log record
        """
        appname = appname or self._appname
        count = self.records_count(appname)
        part, index = self._map_identifier(identifier)

        if identifier > count:
            return

        if part > count - self.max_size:
            record = self._db.lindex(self._rkey % appname, index)
            return j.data.serializers.json.loads(record)

        if self.dump:
            path = j.sals.fs.join_paths(self.dump_dir, appname, "%s.msgpack" % part)
            if j.sals.fs.exists(path):
                records = msgpack.loads(j.sals.fs.read_bytes(path))
                if records and len(records) > index:
                    return j.data.serializers.json.loads(records[index])

    def remove_all_records(self, appname: str):
        """Delete all app's log records
        
        Arguments:
            appname {str} -- app name
        """
        self._db.delete(self._rkey % appname, self._rkey_incr % appname)
        path = j.sals.fs.join_paths(self.dump_dir, appname)

        if self.dump:
            j.sals.fs.rmtree(path)
