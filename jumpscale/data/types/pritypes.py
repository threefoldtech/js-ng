class String:
    def __init__(self, default=None):
        if not default:
            default = ""
        self.default = default

    def check(self, value):
        """Check whether provided value is a string"""
        return isinstance(value, str)

    def from_str(self, value):
        """return string from a string (is basically no more than a check)"""
        return value


class Integer:
    def __init__(self, default=None):
        if not default:
            default = 0
        self.default = self.from_str(default)

    def check(self, value):
        """Check whether provided string represent integer value
        
        Arguments:
            value (str)
        """
        try:
            int(value)
            return True
        except ValueError:
            return False

    def from_str(self, value):
        """get integer value from tha string
        
        Arguments:
            value (str)
        """
        try:
            return int(value)
        except ValueError:
            return None


class Boolean:
    def __init__(self, default=None):
        if not default:
            default = "False"
        self.default = self.from_str(default)

    def check(self, value):
        """Check whether provided string represent Boolean expresion

        Arguments:
            value (str)
        """
        valid_expresions = ["True", "False"]
        return value in valid_expresions

    def from_str(self, value):
        """Get the Boolean value from the string

        Arguments:
            value (str)
        """
        if value == "True":
            return True
        elif value == "False":
            return False
        else:
            return None


class Float:
    def __init__(self, default=None):
        if not default:
            default = 0.0
        self.default = self.from_str(default)

    def check(self, value):
        """Check whether provided string represent integer value
        
        Arguments:
            value (str)
        """
        try:
            float(value)
            return True
        except ValueError:
            return False

    def from_str(self, value):
        """get integer value from tha string
        
        Arguments:
            value (str)
        """
        try:
            return float(value)
        except ValueError:
            return None


class JSObject:
    def __init__(self, default=None):
        default = default or ""
        self.default = self.from_str(default)

    def check(self, value):
        return isinstance(value, str)

    def from_str(self, value):
        return value


class List:
    def __init__(self, default, subtype):
        self.subtype = subtype(default)

    def check(self, value):
        valid = len(value) >= 2 and value[0] == "[" and value[-1] == "]"
        if not valid:
            return False
        # TODO: elements with "," will fail
        elems = value.split(",")
        for e in elems:
            e = e.strip()
            if not self.subtype.check(e):
                return False

        return True

    def from_str(self, value):
        value = value[1:-1]
        lst = []
        elems = value.split(",")
        for e in elems:
            e = e.strip()
            lst.append(self.subtype.from_str(e))
        return lst


def get_js_type(type_str, default_value):
    types = {"": String, "S": String, "I": Integer, "bool": Boolean, "Float": Float, "O": JSObject}
    if type_str[0] != "L":
        return types[type_str](default_value)
    else:
        subtype = types[type_str[1:]]
        return List(default_value, subtype)
