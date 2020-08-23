"""
# To get a new ZDB instance

zcl = j.clients.zdb.get("instance", admin=True, mode="user")

# This will gets an instance with admin capabilities in user mode

"""
from jumpscale.clients.base import Client
from jumpscale.core.base import fields
from enum import Enum


import redis
import struct


class Mode(Enum):
    SEQ = "seq"
    USER = "user"


class ZDBClient(Client):
    addr = fields.String(default="localhost")
    port = fields.Integer(default=9900)
    secret_ = fields.String(default="1234567")
    nsname = fields.String(default="test")
    admin = fields.Boolean(default=False)
    mode = fields.Enum(Mode)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # if not self.secret_:
        #     self.secret_ = j.core.myenv.adminsecret

        assert len(self.secret_) > 5

        if self.admin:
            self.nsname = "default"
        self.type = "ZDB"
        self._redis = None
        self.nsname = self.nsname.lower().strip()

        # if j.data.bcdb._master:
        #     self._model.trigger_add(self._update_trigger)

    def _update_trigger(self, obj, action, **kwargs):
        if action in ["save", "change"]:
            self._redis = None

    @property
    def redis(self):
        if not self._redis:
            pool = redis.ConnectionPool(
                host=self.addr,
                port=self.port,
                password=self.secret_,
                connection_class=ZDBConnection,
                namespace=self.nsname,
                namespace_password=self.secret_,
                admin=self.admin,
            )
            self._redis = _patch_redis_client(redis.Redis(connection_pool=pool))
        return self._redis

    def _key_encode(self, key):
        if self.mode.value == Mode.SEQ.value:
            if key is None:
                key = ""
            else:
                key = struct.pack("<I", key)
        return key

    def _key_decode(self, key):
        if self.mode.value == Mode.SEQ.value:
            key = struct.unpack("<I", key)[0]
        return key

    def set(self, data, key=None):
        key = key or ""
        key = self._key_encode(key)
        res = self.redis.execute_command("SET", key, data)
        if not res:
            return res
        return self._key_decode(res)

    def get(self, key):
        key = self._key_encode(key)
        return self.redis.execute_command("GET", key)

    def exists(self, key):
        key = self._key_encode(key)
        return self.redis.execute_command("EXISTS", key) == 1

    def delete(self, key):
        if not key:
            raise j.exceptions.Value("key must be provided")
        key = self._key_encode(key)
        self.redis.execute_command("DEL", key)

    def flush(self):
        """
        will remove all data from the database DANGEROUS !!!!
        This is only allowed on private and password protected namespace
        You need to select the namespace before running the command.
        :return:
        """
        if not self.nsname in ["default", "system"]:
            self.redis.execute_command("FLUSH")

    def stop(self):
        pass

    @property
    def nsinfo(self):
        cmd = self.redis.execute_command("NSINFO", self.nsname)
        return _parse_nsinfo(cmd.decode())

    def list(self, key_start=None, reverse=False):
        """
        list all the keys in the namespace

        :param key_start: if specified start to walk from that key instead of the first one, defaults to None
        :param key_start: str, optional
        :param reverse: decide how to walk the namespace
                        if False, walk from older to newer keys
                        if True walk from newer to older keys
                        defaults to False
        :param reverse: bool, optional
        :return: list of keys
        :rtype: [str]
        """
        result = []
        for key, data in self.iterate(key_start=key_start, reverse=reverse, keyonly=True):
            result.append(key)
        return result

    def iterate(self, key_start=None, reverse=False, keyonly=False):
        """
        walk over all the namespace and yield (key,data) for each entries in a namespace

        :param key_start: if specified start to walk from that key instead of the first one, defaults to None
        :param key_start: str, optional
        :param reverse: decide how to walk the namespace
                if False, walk from older to newer keys
                if True walk from newer to older keys
                defaults to False
        :param reverse: bool, optional
        :param keyonly: [description], defaults to False
        :param keyonly: bool, optional
        :raises e: [description]
        """

        next = None
        data = None

        if key_start is not None:
            next = self.redis.execute_command("KEYCUR", self._key_encode(key_start))
            if not keyonly:
                data = self.get(key_start)
            yield (key_start, data)

        CMD = "SCANX" if not reverse else "RSCAN"

        while True:
            try:
                if not next:
                    response = self.redis.execute_command(CMD)
                else:
                    response = self.redis.execute_command(CMD, next)
                # format of the response
                # see https://github.com/threefoldtech/0-db/tree/development#scan
            except redis.ResponseError as e:
                if e.args[0] == "No more data":
                    return
                raise e

            (next, results) = response
            for item in results:
                keyb, size, epoch = item
                key_new = self._key_decode(keyb)
                data = None
                if not keyonly:
                    data = self.redis.execute_command("GET", keyb)
                yield (key_new, data)

    @property
    def count(self):
        """
        :return: return the number of entries in the namespace
        :rtype: int
        """
        return self.nsinfo["entries"]

    def ping(self):
        """
        go to default namespace & ping
        :return:
        """
        return self.redis.ping()

    @property
    def next_id(self):
        """
        :return: return the next id
        :rtype: int
        """
        id_bytes = struct.pack("<I", int(self.nsinfo["next_internal_id"], 16))
        return int.from_bytes(id_bytes, byteorder="big", signed=True)


# Helper functions
def _patch_redis_client(redis):
    # don't auto parse response for set, it's not 100% redis compatible
    # 0-db does return a key after in set
    for cmd in ["SET", "DEL"]:
        if cmd in redis.response_callbacks:
            del redis.response_callbacks[cmd]
    return redis


def _parse_nsinfo(raw):
    def empty(line):
        line = line.strip()
        if len(line) <= 0 or line[0] == "#" or ":" not in line:
            return False
        return True

    info = {}
    for line in filter(empty, raw.splitlines()):
        key, val = line.split(":")
        try:
            val = int(val)
            info[key] = val
            continue
        except ValueError:
            pass
        try:
            val = float(val)
            info[key] = val
            continue
        except ValueError:
            pass

        info[key] = str(val).strip()
    return info


class ZDBConnection(redis.Connection):
    """
    ZDBConnection implement the custom selection of namespace
    on 0-DB
    """

    def __init__(self, namespace=None, namespace_password=None, admin=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.namespace = namespace or "default"
        self.namespace_password = namespace_password
        self.admin = admin

    def on_connect(self):
        """
        when a new connection is created, switch to the proper namespace
        """
        self._parser.on_connect(self)

        # if a password is specified, authenticate
        if self.admin and self.password:
            # avoid checking health here -- PING will fail if we try
            # to check the health prior to the AUTH
            self.send_command("AUTH", self.password, check_health=False)
            if redis.connection.nativestr(self.read_response()) != "OK":
                raise redis.connection.AuthenticationError("Invalid Password")

        # if a namespace is specified and it's not default, switch to it
        if self.namespace and not self.admin:
            args = [self.namespace]
            if self.namespace_password:
                args.append(self.namespace_password)

            self.send_command("SELECT", *args)
            if redis.connection.nativestr(self.read_response()) != "OK":
                raise redis.connection.ConnectionError(f"Failed to select namespace {self.namespace}")


class ZDBAdminClient(ZDBClient):
    def auth(self):
        assert self.admin
        if self.secret_:
            # authentication should only happen in zdbadmin client
            self.redis.execute_command("AUTH", self.secret_)

    def namespace_exists(self, name):
        assert self.admin
        self.auth()
        try:
            self.redis.execute_command("NSINFO", name)
            return True
        except Exception as e:
            if not "Namespace not found" in str(e):
                raise j.exceptions.Base("could not check namespace:%s, error:%s" % (name, e))
            return False

    def namespaces_list(self):
        assert self.admin
        self.auth()
        res = self.redis.execute_command("NSLIST")
        return [i.decode() for i in res]

    def namespace_new(self, name, secret=None, maxsize=0, die=False):
        """
        check namespace exists & will return zdb client to that namespace

        :param name:
        :param secret:
        :param maxsize:
        :param die:
        :return:
        """
        assert self.admin
        self.auth()
        if not self.namespace_exists(name):
            self.redis.execute_command("NSNEW", name)
        else:
            if die:
                raise j.exceptions.Base("namespace already exists:%s" % name)

        if secret:
            self.redis.execute_command("NSSET", name, "password", secret)
            self.redis.execute_command("NSSET", name, "public", "no")

        if maxsize != 0:
            self.redis.execute_command("NSSET", name, "maxsize", maxsize)

        ns = j.clients.zdb.client_get(
            name="temp_%s" % name, addr=self.addr, port=self.port, mode=self.mode, secret=secret, namespace=name
        )

        assert ns.ping()
        if secret:
            assert ns.nsinfo["public"] == "no"
        else:
            assert ns.nsinfo["public"] == "yes"

        ns._data.delete()
        return ns

    def namespace_get(self, name, secret=""):
        assert self.admin
        self.auth()
        return self.namespace_new(name, secret)

    def namespace_delete(self, name):
        assert self.admin
        self.auth()
        if self.namespace_exists(name):
            self.redis.execute_command("NSDEL", name)

    def reset(self, ignore=[]):
        """
        dangerous, will remove all namespaces & all data
        :param: list of namespace names not to reset
        :return:
        """
        assert self.admin
        self.auth()
        for name in self.namespaces_list():
            if name not in ["default"] and name not in ignore:
                self.namespace_delete(name)
