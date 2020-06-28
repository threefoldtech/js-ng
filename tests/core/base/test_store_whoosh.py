import datetime

from jumpscale.core.base import Base, fields, StoredFactory
from jumpscale.core.base.store import whooshfts


class Permission(Base):
    is_admin = fields.Boolean()


class Machine(Base):
    ip = fields.IPAddress()


class User(Base):
    id = fields.Integer()
    first_name = fields.String(default="")
    last_name = fields.String(default="")
    emails = fields.List(fields.String())
    permissions = fields.List(fields.Object(Permission))
    custom_config = fields.Typed(dict)
    rating = fields.Integer()
    created_time = fields.DateTime(default=datetime.datetime.now)
    password = fields.Secret()
    machines = fields.Factory(Machine)

    def get_full_name(self):
        name = self.first_name
        if self.last_name:
            name += " " + self.last_name
        return name

    def get_unique_name(self):
        return self.full_name.replace(" ", "") + ".user"

    full_name = fields.String(compute=get_full_name)
    unique_name = fields.String(compute=get_unique_name)


class CustomFactory(StoredFactory):
    STORE = whooshfts.WhooshStore


def test_create_schema_and_search():
    factory = CustomFactory(User)

    a = factory.get("test")
    a.first_name = "test"
    a.last_name = "user"
    a.rating = 1
    a.password = "aaa"
    a.save()

    m = a.machines.get("m1")
    m.ip = "192.168.1.11"
    m.save()

    assert len(factory.list_all()) == 1

    _, total_count, result = factory.find_many(first_name="test")
    assert total_count == 1
    assert next(result).first_name == "test"

    _, total_count, result = factory.find_many(first_name="te*")
    assert total_count == 1
    assert next(result).first_name == "test"

    _, total_count, result = factory.find_many(rating=1)
    assert total_count == 1
    assert next(result).first_name == "test"

    _, total_count, result = factory.find_many(rating=">=1")
    assert total_count == 1
    assert next(result).first_name == "test"

    factory.delete("test")

    assert len(factory.list_all()) == 0
    assert len(a.machines.list_all()) == 0
