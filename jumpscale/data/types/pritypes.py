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


class Boolen:
    def __init__(self, default=None):
        if not default:
            default = "False"
        self.default = self.from_str(default)

    def check(self, value):
        """Check whether provided string represent boolen expresion

        Arguments:
            value (str)
        """
        valid_expresions = ["True", "False"]
        return value in valid_expresions

    def from_str(self, value):
        """Get the boolen value from the string

        Arguments:
            value (str)
        """
        if value == "True":
            return True
        elif value == "False":
            return False
        else:
            return None
