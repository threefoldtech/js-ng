import string
from random import randint, uniform

from jumpscale.core.base import Base, StoredFactory, fields
from jumpscale.core.base.store import etcd
from jumpscale.loader import j
from tests.base_tests import BaseTests

HOST = "127.0.0.1"
ETCD_PORT = 2379


class Address(Base):
    country = fields.String()
    city = fields.String()
    street = fields.String()
    building = fields.Integer()


class Student(Base):
    name = fields.String(default="")
    age = fields.Integer(min=6, max=12)
    grades = fields.List(fields.Float())
    mobile = fields.Tel()
    address = fields.Object(Address)


class EtcdStoredFactory(StoredFactory):
    STORE = etcd.EtcdStore


class EtcdStoreTests(BaseTests):
    def randstr(self):
        return j.data.idgenerator.nfromchoices(10, string.ascii_letters)

    @classmethod
    def setUpClass(cls):
        cls.cmd = None
        if not j.sals.nettools.tcp_connection_test(HOST, ETCD_PORT, 1):
            cls.cmd = j.tools.startupcmd.get("test_etcd_store")
            cls.cmd.start_cmd = "etcd --data-dir /tmp/tests/etcd"
            cls.cmd.ports = [ETCD_PORT]
            cls.cmd.start()
            assert j.sals.nettools.wait_connection_test(HOST, ETCD_PORT, 2) == True, "ETCD didn't start"
        cls.factory = EtcdStoredFactory(Student)

    @classmethod
    def tearDownClass(cls):
        if cls.cmd:
            cls.cmd.stop(wait_for_stop=False)
            j.tools.startupcmd.delete("test_etcd_store")

    def tearDown(self):
        for instance in self.factory.list_all():
            self.factory.delete(instance)

    def test_01_create_find_models(self):
        """Test for creating, finding and deleting models.

        **Test Scenario**

        - Create model and save it.
        - List all instances and check that only one instance found.
        - Get the instance and check that all fields are stored.
        """
        self.info("Create model and save it.")
        instance_name = self.randstr()
        student_1 = self.factory.new(instance_name)

        name = self.randstr()
        age = randint(6, 12)
        mobile = f"{randint(1000000000, 2000000000)}"
        grades = [randint(0, 100), uniform(0, 100)]
        country = self.randstr()
        city = self.randstr()
        street = self.randstr()
        building = randint(1, 100)

        student_details = {"name": name, "age": age, "mobile": mobile, "grades": grades}
        for d in student_details.keys():
            setattr(student_1, d, student_details[d])
        address = {"country": country, "city": city, "street": street, "building": building}
        for a in address.keys():
            setattr(student_1.address, a, address[a])

        self.info("List all instances and check that only one instance found.")
        total_instance = self.factory.list_all()
        self.assertEqual(len(total_instance), 1)
        self.assertIn(instance_name, total_instance)

        self.info("Get the instance and check that all fields are stored.")
        stored_instance = self.factory.get(instance_name)
        for d in student_details:
            self.assertEqual(getattr(stored_instance, d), student_details[d])
        for a in address:
            self.assertEqual(getattr(stored_instance.address, a), address[a])

    def test_02_create_more_instance(self):
        """Test for creating more than one instance.

        **Test Scenario**

        - Create three instances.
        - Check that the instance are stored in etcd.
        - List all instances and check that three instance found.
        """
        self.info("Create three instances.")
        for i in range(3):
            student = self.factory.new(f"instance_{i}")
            student.name = f"student_{i}"
            student.save()

        self.info(self.factory.list_all())

        self.info("List all instances and check that three instance found.")
        total_instances = self.factory.list_all()
        self.assertEqual(len(total_instances), 3)
        for instance in total_instances:
            obj = self.factory.find(instance)
            name = f"student_{instance[-1]}"
            self.assertEqual(obj.name, name)
