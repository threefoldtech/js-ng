import re


class Property:
    def __init__(self):
        self.index = False
        self.index_key = False
        self.index_text = False
        self.unique = False
        self.type = ""
        self.comment = ""
        self.defaultvalue = ""
        self.name = ""


class Schema:
    def __init__(self):
        self.url = ""
        self.system_props = {}
        self.props = {}


def _normalize_string(text):
    """Trims the text, removes all the spaces from text and replaces every sequence of lines with a single line.
    
    Args:
        text (str): The schema definition.
    
    Returns:
        str: The normalized text.
    """
    text = text.strip()
    result = ""
    whitespaces = [" ", "\t"]
    in_comment = False
    for c in text:
        if c == "#":
            in_comment = True
        if c == "\n":
            in_comment = False
        if not in_comment and c in whitespaces:
            continue
        if not in_comment and c == "\n" and result.endswith("\n"):
            continue
        result += c
    return result


def _correct_url_number(text):
    """Checks that the schema definition contains only one url definition.
    
    Args:
        text (str): The schema definition.
    
    Returns:
        bool: Whether only one url is defined.
    """
    url_count = text.count("@url")
    return url_count == 1


def _parse_system_prop(line):
    """Returns the name and value of a system property (The line is preceded by @).
    
    Args:
        line (str): The definition of the system property.
    
    Returns:
        str, str: Pair of name, value.
    """
    return line[1:].split("#")[0].split("=")


def _name_in_correct_form(name):
    """Checks whether the name is a sequence of alphanumberic characters and _ and starts with _.
    
    Args:
        name (str): The name of the property.
    
    Returns:
        bool: True if the name is well formed. False otherwise.
    """
    return name[0] == "_" or name[0].isalpha() and name.replace("_", "").isalnum()


def _is_float(value):
    """Checks if the value is float. Which means it contains two non empty integer parts separated by .
    
    Args:
        value (str): The value.
    
    Returns:
        bool: True if the value represents a float.
    """
    if "." not in value:
        return False
    a, b = value.split(".", 1)
    return a.isdigit() and b.isdigit()


def _infer_type(value):
    """Infers the type from the value.
    one of:
    1. int: contains digits only.
    2. float: two nonempty parts of integers separated by .
    3. string: nonempty sequence of characters inside " or '
    4. bool: literals true or false.
    5. list: equals []
    
    Args:
        value (str): The value which the type is infered from.
    
    Raises:
        RuntimeError: If no types can be infered
    
    Returns:
        str: The type of the value.
    """
    if len(value) >= 2 and (value[0] == '"' and value[-1] == '"' or value[0] == "'" and value[-1] == "'"):
        return "str"
    elif _is_float(value):
        return "float"
    elif value.isdigit():
        return "i"
    elif value == "[]":
        return "ls"
    elif value == "true" or value == "false":
        return "bool"
    else:
        raise RuntimeError(f"Can't infer the type of {value}")


def _parse_prop(line):
    """Parses a line which defines a property.
    
    Args:
        line (str): The property description.
    
    Raises:
        RuntimeError: If the description is malformed.
    
    Returns:
        str, Property: Name of the property and Property object defining the property.
    """
    RE = r"(&?)([^=*]+)((?:\*|\*\*|\*\*\*)?)\=([^(!#]*)((?:\(.*?\))?)((?:\![^#]*)?)((?:#.*)?)"
    match = re.match(RE, line)
    if match is None:
        raise RuntimeError("Can't parse schema")
    prop = Property()
    unique, name, qualifier, default_value, prop_type, pointer_type, comment = match.groups()
    pointer_type = pointer_type[1:] if pointer_type else pointer_type
    prop_type = prop_type[1:-1] if prop_type else prop_type
    comment = comment[1:] if comment else comment
    prop.name = name
    prop.unique = unique == "&"
    prop.index = prop.unique or qualifier == "*"
    prop.index_key = qualifier == "**"
    prop.index_text = qualifier == "***"
    prop.type = prop_type or _infer_type(default_value)
    if len(default_value) >= 2 and (
        default_value[0] == "'" and default_value[-1] == "'" or default_value[0] == '"' and default_value[-1] == '"'
    ):
        default_value = default_value[1:-1]
    prop.defaultvalue = pointer_type or default_value
    prop.comment = comment
    return prop.name, prop


def parse_schema(text):
    """Parses a schema from string.
    
    Args:
        text (str): The schema definition.
    
    Raises:
        RuntimeError: Thrown when the schema can't be parsed.
    
    Returns:
        Schema: Schema object representing the schema.
    """
    text = _normalize_string(text)
    if text.count("@url") != 1:
        raise RuntimeError("The number of urls must be equal to one.")
    lines = text.split("\n")
    schema = Schema()
    for line in lines:
        if line.startswith("@"):
            name, value = _parse_system_prop(line)
            schema.system_props[name] = value
        else:
            name, prop = _parse_prop(line)
            schema.props[name] = prop
    schema.url = schema.system_props["url"]
    return schema

