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
        self.factory = StoredFactory(Client)
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
        self.factory = StoredFactory(Client)
        ret_cl = self.factory.get("test_enum")

        self.assertNotEqual(cl, ret_cl)
        user = ret_cl.users.get("admin")
        self.assertEqual(user.full_name, full_name)
        self.assertEqual(user.unique_name, unique_name)

    def tearDown(self):
        for name in self.factory.store.list_all():
            self.factory.delete(name)
