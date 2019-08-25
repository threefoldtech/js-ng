from jumpscale.clients.base import Client, StoredFactory
from jumpscale.core import fields
from jumpscale.core.base import Base
from jumpscale.god import j


class Email(Base):
    address = fields.String()
    main = fields.Boolean()


class User(Base):
    username = fields.String()
    password = fields.String()

    emails = StoredFactory(Email)


class Github(Client):
    users = StoredFactory(User)

    def hi(self):
        print("hii")
        j.sals.fs.basename("aa")

