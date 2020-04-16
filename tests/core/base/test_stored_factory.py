from enum import Enum
import unittest


# TODO: move fields to fields or types module
from jumpscale.core.base import Base, Factory, StoredFactory, DuplicateError, fields


class Address(Base):
    x = fields.Integer()
    name = fields.String()

    def __init__(self):
        super().__init__()
        self.x = 123


class Wallet(Base):
    ID = fields.Integer()
    addresses = fields.Factory(Address)


class Permission(Base):
    is_admin = fields.Boolean()


class UserType(Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    emails = fields.List(fields.String())
    permissions = fields.List(fields.Object(Permission))
    custom_config = fields.Typed(dict)
    type = fields.Enum(UserType)
    password = fields.Secret()


class Client(Base):
    wallets = fields.Factory(Wallet)
    users = fields.Factory(User)


class TestStoredFactory(unittest.TestCase):
    def setUp(self):
        self.factory = StoredFactory(Client)

    def test_secret_field(self):
        cl = self.factory.get("test_secret")
        user = cl.users.get("user_with_password")

        # do not set password and try to save
        # should not fail
        user.save()
        # do not forget to save the client
        cl.save()

        # get a new factory and check password
        self.factory = StoredFactory(Client)
        cl = self.factory.get("test_secret")
        user = cl.users.get("user_with_password")
        self.assertIsNone(user.password)

        # set password and save
        user.password = "test124"
        user.save()
        cl.save()

        # get a new factory and check password again
        self.factory = StoredFactory(Client)
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
        new_cl = Client()
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
        self.factory = StoredFactory(Client)
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
        self.factory = StoredFactory(Client)
        ret_cl = self.factory.get("test_enum")

        self.assertNotEqual(cl, ret_cl)
        user = ret_cl.users.get("admin")
        self.assertEqual(user.type, UserType.ADMIN)

    def tearDown(self):
        for name in self.factory.store.list_all():
            self.factory.delete(name)
