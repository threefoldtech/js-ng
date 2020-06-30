"""
only test non-stored factories
"""
import datetime
import unittest


# TODO: move fields to fields or types module
from jumpscale.core.base import Base, DuplicateError, fields


class Address(Base):
    x = fields.Integer()
    name = fields.String()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.x = 123


class Wallet(Base):
    ID = fields.Integer()
    addresses = fields.Factory(Address, stored=False)


class RichWallet(Wallet):
    def amount_updated(self, new_value):
        print("got a new amount!", new_value)

    amount = fields.Integer(default=10000000, on_update=amount_updated)


class Client(Base):
    wallets = fields.Factory(RichWallet, stored=False)


class Student(Base):
    ID = fields.Integer()
    name = fields.String()
    email = fields.Email()
    tel = fields.Tel()
    web = fields.URL()
    birthday = fields.Date()


class StudentClient(Base):
    students = fields.Factory(Student, stored=False)


class TestBaseFactory(unittest.TestCase):
    def test_create_with_different_instances(self):
        cl = Client()
        w = cl.wallets.get("aa")
        w.amount = 1000
        self.assertEqual(cl.wallets.count, 1)
        self.assertEqual(w.amount, 1000)

        addr1 = w.addresses.new("mine")
        addr1.x = 456
        addr2 = w.addresses.new("another")
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

    def test_create_instance_with_different_fields(self):
        cl = StudentClient()
        st = cl.students.new("test_student")
        self.assertEqual(cl.students.count, 1)

        st.name = "sam"
        st.email = "sam@gmail.com"
        st.tel = "0122222222"
        st.web = "https://www.sam.com"
        st.birthday = "1990-12-03"

        self.assertEqual(st.name, "sam")
        self.assertEqual(st.email, "sam@gmail.com")
        self.assertEqual(st.tel, "0122222222")
        self.assertEqual(st.web, "https://www.sam.com")
        self.assertEqual(st.birthday, datetime.date(1990, 12, 3))
