"""
this module mostly test creating/storing/reteriving objects/instances

which makes sure every field is serialized correctly
"""
import unittest
from enum import Enum

# TODO: move fields to fields or types module

from jumpscale.core.base import Base, DuplicateError, Factory, StoredFactory, fields
from jumpscale.core.base.store import filesystem, redis, whooshfts, mongo, etcd
from parameterized import parameterized_class
from jumpscale.loader import j

HOST = "127.0.0.1"
REDIS_PORT = 6379
MONGO_PORT = 27017
ETCD_PORT = 2379


class Address(Base):
    x = fields.Integer()
    name = fields.String()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.x = 123


class Car(Base):
    color = fields.String(required=True)
    release_date = fields.DateTime()


class Wallet(Base):
    ID = fields.Integer(required=True)
    origin = fields.Typed(dict, default=dict)
    addresses = fields.Factory(Address)
    key = fields.Bytes()
    email = fields.Email()
    url = fields.URL(required=False, allow_empty=True)
    data = fields.Json(allow_empty=False)


class Permission(Base):
    is_admin = fields.Boolean()


class UserType(Enum):
    USER = "user"
    ADMIN = "admin"


class Greeter:
    def __init__(self, name):
        self.name = name

    def say(self):
        print("hello", self.name)


class User(Base):
    emails = fields.List(fields.String())
    permissions = fields.List(fields.Object(Permission))
    custom_config = fields.Typed(dict)
    type = fields.Enum(UserType)
    password = fields.Secret()

    first_name = fields.String(default="")
    last_name = fields.String(default="")

    def get_full_name(self):
        name = self.first_name
        if self.last_name:
            name += " " + self.last_name
        return name

    def get_unique_name(self):
        return self.full_name.replace(" ", "") + ".user"

    full_name = fields.String(compute=get_full_name)
    unique_name = fields.String(compute=get_unique_name)

    def get_my_greeter(self):
        return Greeter(self.full_name)

    my_greeter = fields.Typed(Greeter, stored=False, compute=get_my_greeter)
    ahmed_greeter = fields.Typed(Greeter, stored=False, default=Greeter("ahmed"))


class Client(Base):
    wallets = fields.Factory(Wallet)
    users = fields.Factory(User)


class FilesystemFactory(StoredFactory):
    STORE = filesystem.FileSystemStore


class RedisFactory(StoredFactory):
    STORE = redis.RedisStore


class WhooshFactory(StoredFactory):
    STORE = whooshfts.WhooshStore


class MongoFactory(StoredFactory):
    STORE = mongo.MongoStore


class EtcdFactory(StoredFactory):
    STORE = etcd.EtcdStore


@parameterized_class(
    [
        {"factory_class": FilesystemFactory},
        {"factory_class": RedisFactory},
        {"factory_class": WhooshFactory},
        {"factory_class": MongoFactory},
        {"factory_class": EtcdFactory},
    ]
)
class TestStoredFactory(unittest.TestCase):

    factory_class = StoredFactory

    @classmethod
    def setUpClass(cls):
        cls.cmd = None
        if issubclass(cls.factory_class, RedisFactory) and not j.sals.nettools.tcp_connection_test(HOST, REDIS_PORT, 1):
            cls.cmd = j.tools.startupcmd.get("test_redis_store")
            cls.cmd.start_cmd = "redis-server"
            cls.cmd.ports = [REDIS_PORT]
            cls.cmd.start()
            assert j.sals.nettools.wait_connection_test(HOST, REDIS_PORT, 2) == True, "Redis didn't start"

        elif issubclass(cls.factory_class, MongoFactory) and not j.sals.nettools.tcp_connection_test(
            HOST, MONGO_PORT, 1
        ):
            j.sals.fs.mkdir("/tmp/mongodb/")
            j.sals.fs.mkdir("/tmp/mongodata/")
            cls.cmd = j.tools.startupcmd.get("test_mongo_store")
            cls.cmd.start_cmd = "mongod --unixSocketPrefix=/tmp/mongodb --dbpath=/tmp/mongodata"
            cls.cmd.ports = [MONGO_PORT]
            cls.cmd.start()
            assert j.sals.nettools.wait_connection_test(HOST, MONGO_PORT, 2) == True, "Mongodb didn't start"

        elif issubclass(cls.factory_class, EtcdFactory) and not j.sals.nettools.tcp_connection_test(HOST, ETCD_PORT, 1):
            cls.cmd = j.tools.startupcmd.get("test_etcd_store")
            cls.cmd.start_cmd = "etcd --data-dir /tmp/tests/etcd"
            cls.cmd.ports = [ETCD_PORT]
            cls.cmd.start()
            assert j.sals.nettools.wait_connection_test(HOST, ETCD_PORT, 2) == True, "ETCD didn't start"

    @classmethod
    def tearDownClass(cls):
        if cls.cmd:
            cls.cmd.stop(wait_for_stop=False)
            if issubclass(cls.factory_class, RedisFactory):
                j.tools.startupcmd.delete("test_redis_store")
            elif issubclass(cls.factory_class, MongoFactory):
                j.tools.startupcmd.delete("test_mongo_store")
                j.sals.fs.rmtree("/tmp/mongodb/")
                j.sals.fs.rmtree("/tmp/mongodata/")
            elif issubclass(cls.factory_class, EtcdFactory):
                j.tools.startupcmd.delete("test_etcd_store")

    def setUp(self):
        self.factory = self.factory_class(Client)
        self.wallets_factory = self.factory_class(Wallet)

    def test_secret_field(self):
        cl = self.factory.get("test_secret")
        user = cl.users.get("user_with_password")

        # do not set password and try to save
        # should not fail
        user.save()
        # do not forget to save the client
        cl.save()

        # get a new factory and check password
        self.factory = self.factory_class(Client)
        cl = self.factory.get("test_secret")
        user = cl.users.get("user_with_password")
        self.assertIsNone(user.password)

        # set password and save
        user.password = "test124"
        user.save()
        cl.save()

        # get a new factory and check password again
        self.factory = self.factory_class(Client)
        cl = self.factory.get("test_secret")
        user = cl.users.get("user_with_password")
        self.assertEqual(user.password, "test124")

    def test_create_stored_factory(self):
        cl = self.factory.get("client")
        w = cl.wallets.get("aa")
        self.assertEqual(cl.wallets.count, 1)

        addr1 = w.addresses.get("mine")
        addr1.x = 456
        addr2 = w.addresses.get("another")
        addr2.x = 680
        self.assertEqual(w.addresses.count, 2)
        w.addresses.delete("another")
        self.assertEqual(w.addresses.count, 1)

        # test duplicates
        with self.assertRaises(DuplicateError):
            w.addresses.new("mine")

        # create another instance
        new_cl = self.factory.get("another_client")
        self.assertEqual(new_cl.wallets.count, 0)

    def test_create_with_list_field(self):
        cl = self.factory.get("test_list")

        # test saving
        user = cl.users.get("auser")

        emails = ["a@b.com"]
        perm1 = Permission()
        perm1.is_admin = True
        permissions = [perm1]

        user.emails = emails
        user.permissions = permissions
        user.save()
        cl.save()

        # reset-factory for now, need to always get from store
        self.factory = self.factory_class(Client)
        ret_cl = self.factory.get("test_list")

        self.assertNotEqual(cl, ret_cl)
        user = ret_cl.users.get("auser")

        self.assertEqual(user.emails, emails)
        self.assertEqual(user.emails, emails)

    def test_create_with_enum_field(self):
        cl = self.factory.get("test_enum")

        # test saving
        user = cl.users.get("admin")
        # default value, still
        self.assertEqual(user.type, UserType.USER)

        # now set and test if it's saved
        user.type = UserType.ADMIN
        user.save()
        cl.save()
        # reset-factory for now, need to always get from store
        self.factory = self.factory_class(Client)
        ret_cl = self.factory.get("test_enum")

        self.assertNotEqual(cl, ret_cl)
        user = ret_cl.users.get("admin")
        self.assertEqual(user.type, UserType.ADMIN)

    def test_create_with_non_stored_fields(self):
        cl = self.factory.get("test_enum")

        # test saving
        user = cl.users.get("admin")
        user.first_name = "abdo"
        user.last_name = "tester"
        user.my_greeter.say()
        user.ahmed_greeter.say()

        with self.assertRaises(fields.ValidationError):
            user.ahmed_greeter = ""

        data = user.to_dict()

        self.assertFalse("my_greeter" in data)
        self.assertFalse("ahmed_greeter" in data)

        user.save()
        cl.save()
        # reset-factory for now, need to always get from store
        self.factory = self.factory_class(Client)
        ret_cl = self.factory.get("test_enum")

        self.assertNotEqual(cl, ret_cl)
        user = ret_cl.users.get("admin")

        data = user.to_dict()

        self.assertFalse("my_greeter" in data)
        self.assertFalse("ahmed_greeter" in data)

    def test_create_with_computed_fields(self):
        cl = self.factory.get("test_enum")

        # test saving
        user = cl.users.get("admin")
        # default value, still
        self.assertEqual(user.type, UserType.USER)

        # now set and test if it's saved
        user.first_name = "ahmed"

        self.assertEqual(user.full_name, user.first_name)
        user.last_name = "mohamed"

        full_name = f"{user.first_name} {user.last_name}"
        self.assertEqual(user.full_name, full_name)

        unique_name = f"{user.first_name}{user.last_name}.user"
        self.assertEqual(user.unique_name, unique_name)
        user.save()
        cl.save()
        # reset-factory for now, need to always get from store
        self.factory = self.factory_class(Client)
        ret_cl = self.factory.get("test_enum")

        self.assertNotEqual(cl, ret_cl)
        user = ret_cl.users.get("admin")
        self.assertEqual(user.full_name, full_name)
        self.assertEqual(user.unique_name, unique_name)

    def test_create_with_bytes_field(self):
        wallet = self.wallets_factory.get("test_bytes")

        # test convert str to bytes
        wallet.key = "aaa"
        self.assertEqual(wallet.key, b"aaa")

        with self.assertRaises(fields.ValidationError):
            wallet.key = 1212121

        wallet.save()

        # reset-factory for now, need to always get from store
        self.factory = self.factory_class(Wallet)
        ret_wallet = self.factory.get("test_bytes")
        self.assertEqual(ret_wallet.key, b"aaa")

    def test_create_with_json_field(self):
        wallet = self.wallets_factory.get("test_json")

        # test convert str to json
        wallet.data = '{"context": "transfer", "id": null}'
        self.assertEqual(wallet.data, '{"context": "transfer", "id": null}')
        wallet.data = [1, 2, 3, 4]
        self.assertEqual(wallet.data, "[1, 2, 3, 4]")

        # test with strings
        wallet.data = '"hamada"'

        # test with list/dict
        wallet.data = '{"numbers": [1, 2, 3, 4]}'
        self.assertEqual(wallet.data, '{"numbers": [1, 2, 3, 4]}')

        with self.assertRaises(fields.ValidationError):
            # not, it's note a json encoded string
            wallet.data = "hamada"

        with self.assertRaises(fields.ValidationError):
            # Base needs to_dict to be json-serializable
            wallet.data = [Wallet]

        with self.assertRaises(fields.ValidationError):
            # bytes are not json serilizable
            wallet.data = {"name": b"bytes name"}

        wallet.save()

        # reset-factory for now, need to always get from store
        self.factory = self.factory_class(Wallet)
        ret_wallet = self.factory.get("test_json")
        self.assertEqual(ret_wallet.data, '{"numbers": [1, 2, 3, 4]}')

    def test_delete_lazy_loaded_before_access(self):
        # create an instance
        wallet = self.wallets_factory.get("test_d1")
        wallet.save()

        # reset factory
        self.wallets_factory = self.factory_class(Wallet)
        # now if we did get or accessed the name directly like
        # self.wallets_factory.test_d1, it will be created
        # but at this moment, it's just a property for wallets factory
        # and the instance itself is not created yet
        # and delete should work too
        self.wallets_factory.delete("test_d1")

    def test_required_fields(self):
        wallet = self.wallets_factory.get("test_required_fields")

        # test required field, cannot set none
        with self.assertRaises(fields.ValidationError):
            wallet.ID = None

        wallet.ID = 12

        # test non-required field, should be able to set and save None
        self.assertEqual(wallet.origin, {})
        wallet.origin = None
        wallet.save()

        self.wallets_factory = self.factory_class(Wallet)
        wallet = self.wallets_factory.get("test_required_fields")
        self.assertEqual(wallet.ID, 12)
        self.assertEqual(wallet.origin, None)

    def test_empty_fields(self):
        # by default, empty values are allowed for string based objects
        wallet = self.wallets_factory.get("test_empty_fields")

        # test setting empty fields
        with self.assertRaises(fields.ValidationError):
            wallet.url = "abcd"

        wallet.url = ""
        wallet.url = None

        # test non-empty fields
        with self.assertRaises(fields.ValidationError):
            # default value is empty, should raise this when getting it
            wallet.data = ""

        wallet.data = '{"a": 1}'
        wallet.save()

        self.wallets_factory = self.factory_class(Wallet)
        wallet = self.wallets_factory.get("test_empty_fields")

        self.assertEqual(wallet.url, None)
        self.assertEqual(wallet.data, '{"a": 1}')

    def test_find(self):
        name = "test_find_with_different_factory"
        wallet = self.wallets_factory.get(name)
        new_factory = self.factory_class(Wallet)

        # not yet saved
        self.assertIsNone(new_factory.find(name))

        wallet.save()
        self.assertIsNotNone(new_factory.find(name))

    def test_field_name_in_exception(self):
        cars = self.factory_class(Car)
        bmw = cars.get("bmw")
        with self.assertRaisesRegex(fields.ValidationError, "^color: *"):
            bmw.save()

        with self.assertRaisesRegex(fields.ValidationError, "^release_date: *"):
            bmw.release_date = "qwe"

    def test_create_instance_with_sub_factories_without_factory(self):
        client = Client()
        self.assertEqual(client.users.count, 0)

    def tearDown(self):
        for name in self.factory.list_all():
            self.factory.delete(name)

        for name in self.wallets_factory.list_all():
            self.wallets_factory.delete(name)
