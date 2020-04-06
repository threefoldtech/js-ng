import unittest
from jumpscale.core.base import fields, ValidationError


class TestFields(unittest.TestCase):
    # Email tests
    def test_create_email_success(self):
        """Success scenario for email validation"""
        email = fields.Email("test@gmail.com")
        self.assertEqual(email.default, "test@gmail.com")
        self.assertIsNone(email.validate("test@gmail.com"))

    def test_create_email_failure(self):
        """Failure scenario for email validation"""
        email = fields.Email("test@gmail.com")
        self.assertEqual(email.default, "test@gmail.com")
        with self.assertRaises(ValidationError):
            email.validate("test")

    # Path tests
    def test_create_path_success(self):
        """Success scenario for path validation"""
        path = fields.Path("/home")
        self.assertEqual(path.default, "/home")
        self.assertIsNone(path.validate("/home"))

    def test_create_path_failure(self):
        """Failure scenario for path validation"""
        path = fields.Path("/home")
        self.assertEqual(path.default, "/home")
        with self.assertRaises(ValidationError):
            path.validate("test")

    # URL tests
    def test_create_url_success(self):
        """Success scenario for URL validation"""
        url = fields.URL("https://www.test.com")
        self.assertEqual(url.default, "https://www.test.com")
        self.assertIsNone(url.validate("https://www.test.com"))

    def test_create_url_failure(self):
        """Failure scenario for URL validation"""
        url = fields.URL("https://www.test.com")
        self.assertEqual(url.default, "https://www.test.com")
        with self.assertRaises(ValidationError):
            url.validate("test")

    # Tel tests
    def test_create_tel_success(self):
        """Success scenario for tel validation"""
        tel = fields.Tel("012-222-22222")
        self.assertEqual(tel.default, "01222222222")
        self.assertIsNone(tel.validate("012-222-22222"))

    def test_create_tel_failure(self):
        """Failure scenario for tel validation"""
        tel = fields.Tel("012-222-22222")
        self.assertEqual(tel.default, "01222222222")
        with self.assertRaises(ValidationError):
            tel.validate("test")

    # IPaddress tests
    def test_create_ipaddress_ipv4_success(self):
        """Success scenario for ipaddress ipv4 validation"""
        ipaddress = fields.IPAddress("192.168.0.1")
        self.assertEqual(ipaddress.default, "192.168.0.1")
        self.assertIsNone(ipaddress.validate("192.168.0.1"))

    def test_create_ipaddress_ipv6_success(self):
        """Success scenario for ipaddress ipv6 validation"""
        ipaddress = fields.IPAddress("2001:db8::")
        self.assertEqual(ipaddress.default, "2001:db8::")
        self.assertIsNone(ipaddress.validate("2001:db8::"))

    def test_create_ipaddress_network_success(self):
        """Success scenario for ipaddress network validation"""
        ipaddress = fields.IPAddress("192.168.0.0/28")
        self.assertEqual(ipaddress.default, "192.168.0.0/28")
        self.assertIsNone(ipaddress.validate("192.168.0.0/28"))

    def test_create_ipaddress_failure(self):
        """Failure scenario for ipaddress validation"""
        ipaddress = fields.IPAddress("192.168.0.1")
        self.assertEqual(ipaddress.default, "192.168.0.1")
        with self.assertRaises(ValidationError):
            ipaddress.validate("test")

    # Datetime tests
    def test_create_datetime_success(self):
        """Success scenario for datetime validation"""
        datetime = fields.DateTime("2020-12-03 12:30")
        self.assertEqual(datetime.default, "2020-12-03 12:30")
        self.assertIsNone(datetime.validate("2020-12-03 12:30"))

    def test_create_datetime_failure(self):
        """Failure scenario for DateTime validation"""
        datetime = fields.DateTime("2020-12-03 12:30")
        self.assertEqual(datetime.default, "2020-12-03 12:30")
        with self.assertRaises(ValidationError):
            datetime.validate("1992/2/22")

    # Date tests
    def test_create_date_success(self):
        """Success scenario for date validation"""
        date = fields.Date("2020-12-03")
        self.assertEqual(date.default, "2020-12-03")
        self.assertIsNone(date.validate("2020-12-03"))

    def test_create_date_failure(self):
        """Failure scenario for Date validation"""
        date = fields.Date("2020-12-03")
        self.assertEqual(date.default, "2020-12-03")
        with self.assertRaises(ValidationError):
            date.validate("12:30")

    # Time tests
    def test_create_time_success(self):
        """Success scenario for time validation"""
        time = fields.Time("12:30")
        self.assertEqual(time.default, "12:30")
        self.assertIsNone(time.validate("12:30"))

    def test_create_Time_failure(self):
        """Failure scenario for time validation"""
        time = fields.Time("12:30")
        self.assertEqual(time.default, "12:30")
        with self.assertRaises(ValidationError):
            time.validate("2020-12-03")
