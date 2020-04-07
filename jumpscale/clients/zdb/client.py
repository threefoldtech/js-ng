from jumpscale.clients.base import Client
from jumpscale.core.base import Base, fields

import redis
import struct


class ZDBClient(Base):
    name = fields.String(default="test_instance")
    addr = fields.String(default="localhost")
    port = fields.Integer(default=9900)
    secret_ = fields.String(default="")
    nsname = fields.String(default="test")
    admin = fields.Boolean(default=False)
    # TODO: Replace it with enum  data type of (seq) and (user)
    mode = fields.String(default="seq")

    def __init__(self):
        super().__init__()
        # if not self.secret_:
        #     self.secret_ = j.core.myenv.adminsecret

        assert len(self.secret_) > 5

        if self.admin:
            self.nsname = "default"
        self.type = "ZDB"
        self._redis = None
        self.nsname = self.nsname.lower().strip()

        # self._logger_enable()

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


# Helper functions
def _patch_redis_client(redis):
    # don't auto parse response for set, it's not 100% redis compatible
    # 0-db does return a key after in set
    for cmd in ["SET", "DEL"]:
        if cmd in redis.response_callbacks:
            del redis.response_callbacks[cmd]
    return redis


class ZDBAdminClient(Base):
    name = fields.String(default="test_instance")
    addr = fields.String(default="localhost")
    port = fields.Integer(default=9900)
    secret_ = fields.String(default="")
    nsname = fields.String(default="test")
    admin = fields.Boolean(default=False)
    # TODO: Replace it with enum  data type of (seq) and (user)
    mode = fields.String(default="seq")

    def __init__(self):
        super().__init__()

    def auth(self):
        assert self.admin
        if self.secret_:
            # authentication should only happen in zdbadmin client
            self._log_debug("AUTH in namespace %s" % (self.nsname))
            self.redis.execute_command("AUTH", self.secret_)


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

