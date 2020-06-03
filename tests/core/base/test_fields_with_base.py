"""testing base with some fields, set/get,  validation and conversion from/to raw values"""
import datetime
import enum
import unittest

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
