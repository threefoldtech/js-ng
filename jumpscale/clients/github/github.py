from jumpscale.clients.base import Client
from jumpscale.core.base import Base, fields
from jumpscale.god import j


class Email(Base):
    address = fields.String()
    main = fields.Boolean()


class User(Base):
    username = fields.String()
    password = fields.String()

    emails = fields.Factory(Email)


class Github(Client):
    users = fields.Factory(User)

    def hi(self):
        print("hii")
        j.sals.fs.basename("aa")

