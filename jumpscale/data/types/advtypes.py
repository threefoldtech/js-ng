import re


class Email:
    def __init__(self, default=None):
        if not default:
            default = ""
        self.default = default
        self.regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    def check(self, value):
        return re.search(self.regex, value) is not None

    def from_str(self, value):
        return value


class Path:
    def __init__(self, default=None):
        if not default:
            default = ""
        self.default = default
        self.regex = r"^(?:\.{2})?(?:\/\.{2})*(\/[a-zA-Z0-9]+)+$"

    def check(self, value):
        value = self._clean(value)
        return re.search(self.regex, value) is not None

    def from_str(self, value):
        return value

    def _clean(self, value):
        if value is not None:
            return value.replace("\\", "/")


class URL:
    def __init__(self, default=None):
        if not default:
            default = ""
        self.default = default
        self.regex = r"^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$"

    def check(self, value):
        return re.search(self.regex, value) is not None

    def from_str(self, value):
        return value


class Tel:
    def __init__(self, default=None):
        if not default:
            default = ""
        self.default = default
        self.regex = r"^\+?[0-9]{6,15}(?:x[0-9]+)?$"

    def check(self, value):
        value = self._clean(value)
        return re.search(self.regex, value) is not None

    def from_str(self, value):
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
        self.regex = r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/[0-9]{1,2}"

    def check(self, value):
        return re.search(self.regex, value) is not None

    def from_str(self, value):
        return value


class DateTime:
    """Support yyyy-mm-dd hh:mm format"""

    def __init__(self, default=None):
        if not default:
            default = ""
        self.default = default
        self.regex = r"[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1]) (2[0-3]|[01][0-9]):[0-5][0-9]"

    def check(self, value):
        return re.search(self.regex, value) is not None

    def from_str(self, value):
        return value


class Date:
    """Support yyyy-mm-dd format"""

    def __init__(self, default=None):
        if not default:
            default = ""
        self.default = default
        self.regex = r"[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])"

    def check(self, value):
        return re.search(self.regex, value) is not None

    def from_str(self, value):
        return value


class Time:
    """Support hh:mm format"""

    def __init__(self, default=None):
        if not default:
            default = ""
        self.default = default
        self.regex = r"(2[0-3]|[01][0-9]):[0-5][0-9]"

    def check(self, value):
        return re.search(self.regex, value) is not None

    def from_str(self, value):
        return value


class Duration:
    """Support (int)d (int)h (int)m (int)s format"""

    def __init__(self, default=None):
        if not default:
            default = ""
        self.default = default
        self.regex = r"((\d{1,2}d\s?)?(\d{1,2}h\s?)?(\d{1,2}m\s?)?(\d{1,2}s\s?)?)|\d{1,2}"

    def check(self, value):
        return re.search(self.regex, value) is not None

    def from_str(self, value):
        return value
