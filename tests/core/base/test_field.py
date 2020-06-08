"""testing fields validation and conversion from/to raw values"""

import unittest
import datetime

from jumpscale.core.base import fields, ValidationError


class TestFields(unittest.TestCase):
    def test_bool(self):
        field = fields.Boolean()
        self.assertEqual(field.from_raw("yes"), True)
        self.assertEqual(field.from_raw("off"), False)
        self.assertEqual(field.from_raw(complex(1, 2)), True)
        self.assertEqual(field.from_raw(0), False)

        with self.assertRaises(ValidationError):
            field.validate("habd kteer")

    def test_int(self):
        field = fields.Integer()
        self.assertEqual(field.from_raw("1212"), 1212)
        self.assertEqual(field.from_raw("  12"), 12)

        with self.assertRaises(ValidationError):
            field.validate(1.4)

        with self.assertRaises(ValidationError):
            field.validate("hbd akter")

    def test_int(self):
        field = fields.Float()
        self.assertEqual(field.from_raw("1212.2"), 1212.2)
        self.assertEqual(field.from_raw("  12.2"), 12.2)

        with self.assertRaises(ValidationError):
            field.validate(1)

        with self.assertRaises(ValidationError):
            field.validate("more hbd here")

    # Email tests
    def test_email(self):
        email = fields.Email(default="test@gmail.com")
        self.assertEqual(email.default, "test@gmail.com")
        email.validate("test@gmail.com")

        with self.assertRaises(ValidationError):
            email.validate("test")

    # Path tests
    def test_url(self):
        """Success scenario for path validation"""
        path = fields.Path("/home")
        self.assertEqual(path.default, "/home")
        self.assertIsNone(path.validate("/home"))

        path = fields.Path("/home")
        self.assertEqual(path.default, "/home")
        with self.assertRaises(ValidationError):
            path.validate("test")

    # URL tests
    def test_url(self):
        """Success scenario for URL validation"""
        url = fields.URL("https://www.test.com")
        self.assertEqual(url.default, "https://www.test.com")
        self.assertIsNone(url.validate("https://www.test.com"))

        """Failure scenario for URL validation"""
        url = fields.URL("https://www.test.com")
        self.assertEqual(url.default, "https://www.test.com")
        with self.assertRaises(ValidationError):
            url.validate("test")

    # Tel tests
    def test_tel(self):
        """Success scenario for tel validation"""
        tel = fields.Tel(default="01222222222")
        self.assertEqual(tel.default, "01222222222")

        """Failure scenario for tel validation"""
        tel = fields.Tel(default="012-222-22222")
        self.assertEqual(tel.from_raw(tel.default), "01222222222")
        with self.assertRaises(ValidationError):
            tel.validate("test")

    # IPaddress tests
    def test_ipaddress_v4(self):
        """Success scenario for ipaddress ipv4 validation"""
        ipaddress = fields.IPAddress("192.168.0.1")
        self.assertEqual(ipaddress.default, "192.168.0.1")
        self.assertIsNone(ipaddress.validate("192.168.0.1"))

        """Failure scenario for ipaddress validation"""
        ipaddress = fields.IPAddress("192.168.0.1")
        self.assertEqual(ipaddress.default, "192.168.0.1")
        with self.assertRaises(ValidationError):
            ipaddress.validate("test")

    def test_ipaddress_v6(self):
        """Success scenario for ipaddress ipv6 validation"""
        ipaddress = fields.IPAddress("2001:db8::")
        self.assertEqual(ipaddress.default, "2001:db8::")
        self.assertIsNone(ipaddress.validate("2001:db8::"))

    def test_ipaddress_network(self):
        """Success scenario for ipaddress network validation"""
        ipaddress = fields.IPRange("192.168.0.0/28")
        self.assertEqual(ipaddress.default, "192.168.0.0/28")
        self.assertIsNone(ipaddress.validate("192.168.0.0/28"))

    # Datetime tests
    def test_datetime(self):
        """Success scenario for datetime validation"""
        value = "2020-12-03 12:30"
        dt_field = fields.DateTime(default=value)
        from_raw = dt_field.from_raw(dt_field.default)
        dt_obj = datetime.datetime.strptime(value, dt_field.format).replace(tzinfo=datetime.timezone.utc)
        self.assertEqual(from_raw, dt_obj)

        # check conversion (utc)
        self.assertEqual(dt_field.to_raw(dt_obj), 1606998600.0)
        self.assertEqual(dt_field.from_raw(1606998600.0), dt_obj)

        """Failure scenario for DateTime validation"""
        with self.assertRaises(ValidationError):
            dt_field.validate("1992/2/22")

    # Date tests
    def testest_date(self):
        """Success scenario for date validation"""
        value = "2020-12-03"
        timestamp = 1606953600

        dt_field = fields.Date(default=value)
        from_raw = dt_field.from_raw(dt_field.default)
        dt_obj = datetime.datetime.strptime(value, dt_field.format).replace(tzinfo=datetime.timezone.utc)
        dt_obj = dt_obj.date()
        self.assertEqual(from_raw, dt_obj)

        # check conversion
        self.assertEqual(dt_field.to_raw(dt_obj), timestamp)
        self.assertEqual(dt_field.from_raw(timestamp), dt_obj)

        """Failure scenario for Date validation"""
        date = fields.Date("2020-12-03")
        with self.assertRaises(ValidationError):
            date.validate("12:30")

    # Time tests
    def test_time(self):
        """Success scenario for time validation"""
        value = "12:30"
        t_field = fields.Time(default=value)
        from_raw = t_field.from_raw(t_field.default)
        t_obj = datetime.datetime.strptime(value, t_field.format).replace(tzinfo=datetime.timezone.utc).time()
        self.assertEqual(from_raw, t_obj)
        # check conversion
        # -2208943800 => 1/1/1 12:30:00
        # arrow does this to deal with time only, sets 1/1/1 as a date if time only us given)
        self.assertEqual(t_field.to_raw(t_obj), -2208943800)
        self.assertEqual(t_field.from_raw(-2208943800), t_obj)

        """Failure scenario for time validation"""
        time = fields.Time("12:30")
        self.assertEqual(time.default, "12:30")
        with self.assertRaises(ValidationError):
            time.validate("2020-12-03")
