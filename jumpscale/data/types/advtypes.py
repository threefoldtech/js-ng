import re


class Email:
    def __init__(self, default=None):
        if not default:
            default = ""
        self.default = default
        self.regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    def check(self, value):
        """Check whether provided value is a valid email representation
        Arguments:
            value (str)
        Returbs:
            Boolean expresion"""
        return re.search(self.regex, value) is not None

    def from_str(self, value):
        """get the value from the string
        Arguments:
            value (str)
        Returbs:
            value (str)"""
        return value


class Path:
    def __init__(self, default=None):
        if not default:
            default = ""
        self.default = default
        self.regex = r"^(/[^/ ]*)+/?$"

    def check(self, value):
        """Check whether provided value is a valid path representation
        Arguments:
            value (str)
        Returbs:
            Boolean expresion"""
        return re.search(self.regex, value) is not None

    def from_str(self, value):
        """get the value from the string
        Arguments:
            value (str)
        Returbs:
            value (str)"""
        return value


class URL:
    def __init__(self, default=None):
        if not default:
            default = ""
        self.default = default
        self.regex = r"^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$"

    def check(self, value):
        """Check whether provided value is a valid URL representation
        Arguments:
            value (str)
        Returbs:
            Boolean expresion"""
        return re.search(self.regex, value) is not None

    def from_str(self, value):
        """get the value from the string
        Arguments:
            value (str)
        Returbs:
            value (str)"""
        return value


class Tel:
    def __init__(self, default=None):
        if not default:
            default = ""
        self.default = default
        self.regex = r"^\+?[0-9]{6,15}(?:x[0-9]+)?$"

    def check(self, value):
        """Check whether provided value is a valid Telephone number representation
        Arguments:
            value (str)
        Returbs:
            Boolean expresion"""
        value = self._clean(value)
        return re.search(self.regex, value) is not None

    def from_str(self, value):
        """get the value from the string
        Arguments:
            value (str)
        Returbs:
            value (str)"""
        return value

    def _clean(self, value):
        if value is not None:
            value = value.replace(",", "")
            value = value.replace("-", "")
            value = value.replace("(", "")
            value = value.replace(")", "")
            value = value.replace(" ", "")
            return value


class IPAddress:
    def __init__(self, default=None):
        if not default:
            default = ""
        self.default = default
        self.regex = r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}"

    def check(self, value):
        """Check whether provided value is a valid IPaddress representation
        Arguments:
            value (str)
        Returbs:
            Boolean expresion"""
        return re.search(self.regex, value) is not None

    def from_str(self, value):
        """get the value from the string
        Arguments:
            value (str)
        Returbs:
            value (str)"""
        return value


class DateTime:
    """Supported format: yyyy-mm-dd hh:mm"""

    def __init__(self, default=None):
        if not default:
            default = ""
        self.default = default
        self.regex = r"^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1]) (2[0-3]|[01][0-9]):[0-5][0-9]$"

    def check(self, value):
        """Check whether provided value is a valid datetime representation
        Arguments:
            value (str)
        Returbs:
            Boolean expresion"""
        return re.search(self.regex, value) is not None

    def from_str(self, value):
        """get the value from the string
        Arguments:
            value (str)
        Returbs:
            value (str)"""
        return value


class Date:
    """Support yyyy-mm-dd format"""

    def __init__(self, default=None):
        if not default:
            default = ""
        self.default = default
        self.regex = r"[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])"

    def check(self, value):
        """Check whether provided value is a valid date representation
        Arguments:
            value (str)
        Returbs:
            Boolean expresion"""
        return re.search(self.regex, value) is not None

    def from_str(self, value):
        """get the value from the string
        Arguments:
            value (str)
        Returbs:
            value (str)"""
        return value


class Time:
    """Supported format : hh:mm"""

    def __init__(self, default=None):
        if not default:
            default = ""
        self.default = default
        self.regex = r"(2[0-3]|[01][0-9]):[0-5][0-9]"

    def check(self, value):
        """Check whether provided value is a valid time representation
        Arguments:
            value (str)
        Returbs:
            Boolean expresion"""
        return re.search(self.regex, value) is not None

    def from_str(self, value):
        """Get the value from string
            value (str)
        Returbs:
            value (str)"""
        return value


class Duration:
    """Supported format : (n)y (n)m (n)d (n)h (n)m (n)s"""

    def __init__(self, default=None):
        if not default:
            default = ""
        self.default = default
        self.regex = r"((\d{1,2}y\s?)?(\d{1,2}m\s?)?(\d{1,2}d\s?)?(\d{1,2}h\s?)?(\d{1,2}m\s?)?(\d{1,2}s\s?)?)|\d{1,2}"

    def check(self, value):
        """Check whether provided value is a valid duration representation
        Arguments:
            value (str)
        Returbs:
            Boolean expresion"""
        return re.search(self.regex, value) is not None

    def from_str(self, value):
        """Get the value from string
            value (str)
        Returbs:
            value (str)"""
        return value
