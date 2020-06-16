"""testing base with some fields, set/get,  validation and conversion from/to raw values"""
import datetime
import enum
import unittest
import uuid

from jumpscale.core.base import Base, fields, ValidationError


class Permission(Base):
    is_admin = fields.Boolean()


class User(Base):
    id = fields.Integer()
    first_name = fields.String(default="")
    last_name = fields.String(default="")
    emails = fields.List(fields.String())
    permissions = fields.List(fields.Object(Permission))
    custom_config = fields.Typed(dict)
    rating = fields.Float()
    time = fields.DateTime(default=datetime.datetime.now)

    def get_full_name(self):
        name = self.first_name
        if self.last_name:
            name += " " + self.last_name
        return name

    def get_unique_name(self):
        return self.full_name.replace(" ", "") + ".user"

    full_name = fields.String(compute=get_full_name)
    unique_name = fields.String(compute=get_unique_name)


class Colors(enum.Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


class Car(Base):
    color = fields.Enum(Colors)


class Server(Base):
    host = fields.IPAddress()
    network = fields.IPRange()
    port = fields.Port()
    uid = fields.GUID()
    key = fields.Bytes()


class Guest(Base):
    name = fields.String()


class Host(Base):
    guest = fields.Object(Guest)


class TestBaseWithFields(unittest.TestCase):
    def test_integer_field(self):
        user = User()
        user.id = "111"
        self.assertEqual(user.id, 111)

        with self.assertRaises(ValidationError):
            user.id = "xxx"

    def test_float_field(self):
        user = User()
        user.rating = "11.2"
        self.assertEqual(user.rating, 11.2)

        with self.assertRaises(ValidationError):
            user.rating = "xxx"

    def test_list_field(self):
        user = User()
        self.assertEqual(user.emails, [])
        user.emails = ["a@b.com", "c@d.com"]

        permission_1 = Permission()
        permission_1.is_admin = True
        user.permissions = [permission_1]

        with self.assertRaises(ValidationError):
            user.permissions = [True]

    def test_typed_field(self):
        user = User()

        user.custom_config = {"name": None}

        with self.assertRaises(ValidationError):
            user.custom_config = Permission()

    def test_enum_field(self):
        car = Car()
        car.color = Colors.RED

        # set with a raw value
        car.color = "blue"
        self.assertEqual(car.color, Colors.BLUE)

        with self.assertRaises(ValidationError):
            car.color = "xyz"

    def test_from_dict(self):
        user = User.from_dict({"id": 10, "rating": 1.5})

        self.assertEqual(user.id, 10)
        self.assertEqual(user.rating, 1.5)

    def test_to_dict(self):
        user = User()
        user.rating = "11.2"

        data = user.to_dict()
        self.assertEqual(data["rating"], 11.2)

    def test_computed_field(self):
        u = User()
        u.first_name = "ahmed"

        self.assertEqual(u.full_name, u.first_name)
        u.last_name = "mohamed"

        full_name = f"{u.first_name} {u.last_name}"
        self.assertEqual(u.full_name, full_name)

        unique_name = f"{u.first_name}{u.last_name}.user"
        self.assertEqual(u.unique_name, unique_name)

    def test_callable_defaults(self):
        u = User()
        # once accessed, the value is evaluated
        time = u.time

        self.assertEqual(type(u.time), datetime.datetime)
        self.assertEqual(time, u.time)

    def test_port_field(self):
        server = Server()
        server.port = "9999"

        self.assertEqual(server.port, 9999)

        server.port = 21
        self.assertEqual(server.port, 21)

        with self.assertRaises(ValidationError):
            server.port = -111

        with self.assertRaises(ValidationError):
            server.port = 928392832

    def test_guid_field(self):
        server = Server()

        # auto generated uuid v4 str
        self.assertEqual(type(server.uid), str)

        str_uuid = "12345678-1234-4678-9234-567812345678"

        # test with bytes
        server.uid = b"\x12\x34\x56\x78" * 4
        self.assertEqual(server.uid, str_uuid)

        # test with int
        server.uid = 0x12345678123456781234567812345678
        self.assertEqual(server.uid, str_uuid)

        # test with str too
        server.uid = str_uuid.replace("-", "")
        self.assertEqual(server.uid, str_uuid)

        # test with UUID object
        server.uid = uuid.UUID(int=0x12345678123456781234567812345678, version=4)
        self.assertEqual(server.uid, str_uuid)

        with self.assertRaises(ValidationError):
            server.uid = -1234

        with self.assertRaises(ValidationError):
            server.uid = "aaaaaa"

    def test_ip_address_field(self):
        server = Server()
        server.host = "localhost"
        self.assertEqual(server.host, "127.0.0.1")
        server.host = "192.168.1.1"

        with self.assertRaises(ValidationError):
            server.host = 0

        with self.assertRaises(ValidationError):
            server.host = "182.111.11"

        with self.assertRaises(ValidationError):
            server.host = "192.168.0.0/28"

    def test_ip_range_field(self):
        server = Server()
        server.network = "192.168.0.0/28"
        server.network = "2001:db00::0/24"
        server.network = "2001:db00::1/24"

        with self.assertRaises(ValidationError):
            server.network = "192.168.23.300/28"

        with self.assertRaises(ValidationError):
            server.network = "2001:db00::0/ffff:ff00:"

    def test_object_field_default(self):
        host1 = Host()
        host2 = Host()

        guest1 = Guest()
        guest2 = Guest()

        self.assertNotEqual(id(host1), id(host2))
        self.assertNotEqual(id(guest1), id(guest2))

        self.assertNotEqual(id(host1.guest), id(host2.guest))

        host1.guest.name = "test1"
        host2.guest.name = "test2"

        self.assertNotEqual(host1.guest.name, host2.guest.name)
