import ast


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
        """Check whether provided string represent JSObject value. (Any string will do).
        
        Arguments:
            value (str)
        """
        return isinstance(value, str)

    def from_str(self, value):
        """Return value as is.
        
        Arguments:
            value (str)
        """
        return value


class List:
    def __init__(self, default, subtype):
        self.subtype = subtype
        default = default or "[]"
        self.default = self.from_str(default)

    def _deep_check(self, value):
        """Check that the value represents a list with proper elements of the specified subtype.
        
        Args:
            value (list): The list to be checked.
        
        Returns:
            Boolean: True if the list is valid.
        """
        if not isinstance(value, list):
            return False
        for e in value:
            if isinstance(self.subtype, List) and not self.subtype._deep_check(e):
                return False
            elif not isinstance(self.subtype, List) and not self.subtype.check(str(e)):
                return False
        return True

    def check(self, value):
        """Check that the value represents a list with proper elements of the specified subtype.
        
        Args:
            value (list): The list to be checked.
        
        Returns:
            Boolean: True if the list is valid.
        """
        valid = len(value) >= 2 and value[0] == "[" and value[-1] == "]"
        if not valid:
            return False
        try:
            return self._deep_check(ast.literal_eval(value))
        except:
            return False
        return True

    def _deep_parse(self, value):
        """parses the subelements (if they are of different python type it's converted using the subtype parser)
        
        Args:
            value (list): The list to be parsed.
        
        Returns:
            list: The parsed list.
        """
        result = []
        if isinstance(self.subtype, List):
            for i, e in enumerate(value):
                value[i] = self.subtype._deep_parse(e)
        else:
            for i, e in enumerate(value):
                value[i] = self.subtype.from_str(str(e))
        return value

    def from_str(self, value):
        """parses the string value into a list.
        
        Args:
            value (str): The string to be parsed.
        
        Returns:
            list: The parsed list.
        """
        if isinstance(self.subtype, JSObject):
            return value
        else:
            return self._deep_parse(ast.literal_eval(value))


def get_js_type(type_str, default_value=None):
    """Gets the js type from a string.

    1. "S" -> String
    2. "B" -> Boolean
    3. "I" -> Integer
    4. "O" -> JSObject
    4. "F" -> Float
    5. "L.*" -> List with subtype .*
    6. "" -> empty defaults to String
    
    Args:
        type_str (str): type description.
        default_value (any, optional): The default value. Defaults to None.
    
    Returns:
        Object: A js type object.
    """
    types = {"": String, "S": String, "I": Integer, "B": Boolean, "F": Float, "O": JSObject}
    if len(type_str) == 0 or type_str[0] != "L":
        return types[type_str](default_value)
    else:
        subtype = type_str[1:]
        return List(default_value, get_js_type(subtype))
