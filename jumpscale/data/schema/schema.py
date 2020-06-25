import re
from jumpscale.loader import j


def pascalify_name(name):
    return "".join([x.capitalize() for x in name.replace("_", "-").split("-")])


class Property:
    def __init__(self):
        self.index = False
        self.index_key = False
        self.index_text = False
        self.unique = False
        self.type = None
        self.comment = ""
        self.defaultvalue = ""
        self.name = ""
        self.pointer_type = ""
        self.prop_type = ""

    @classmethod
    def get_id_prop(cls):
        prop = cls()
        prop.prop_type = "I"
        prop.name = "id"
        prop.type = j.data.types.get_js_type(prop.prop_type)
        return prop

    def __repr__(self):
        return str(self.__dict__)

    __str__ = __repr__

    @property
    def url_to_class_name(self):
        url = self.defaultvalue
        urlparts = url.split(".")
        return "".join(x.capitalize() for x in urlparts)


class Schema:
    def __init__(self):
        self.url = ""
        self.system_props = {}
        self.props = {"id": Property.get_id_prop()}

    @property
    def url_to_class_name(self):
        return "".join(x.capitalize() for x in self.url.split("."))

    def get_enums_required(self):
        enums = []
        for prop_name, prop in self.props.items():
            if prop.prop_type == "E":
                cleanname = pascalify_name(prop.name)
                enums.append({"name": cleanname, "vals": [pascalify_name(x) for x in prop.defaultvalue.split(",")]})
        return enums

    def get_classes_required(self):
        classes = []
        for prop_name, prop in self.props.items():
            if prop.prop_type in ["O", "LO"] and "." in prop.defaultvalue:
                classes.append(prop.url_to_class_name)
        return classes

    def get_dependencies(self):

        return {enum: self.get_enums_required(), classes: self.get_classes_requireds()}


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
    in_string = False
    string_char = None
    for c in text:
        if c == "#":
            in_comment = True
        if c == "\n":
            in_comment = False
        if c == '"' or c == "'":
            if in_string and c == string_char:
                in_string = False
            elif not in_string and not in_comment:
                in_string = True
                string_char = c

        if not in_comment and not in_string and c in whitespaces:
            continue
        if c == "\n" and result.endswith("\n"):
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
    5. list: equals surrounded by [].

    Args:
        value (str): The value which the type is infered from.

    Raises:
        RuntimeError: If no types can be infered

    Returns:
        str: The type of the value.
    """
    if len(value) >= 2 and (value[0] == '"' and value[-1] == '"' or value[0] == "'" and value[-1] == "'"):
        return "S"
    elif _is_float(value):
        return "F"
    elif value.isdigit():
        return "I"
    elif value == "[]":
        return "L"
    elif value == "true" or value == "false":
        return "B"
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
    if name == "id":
        raise NameError("id is reserved and can't be a name of property.")
    pointer_type = pointer_type[1:] if pointer_type else pointer_type
    prop.pointer_type = pointer_type
    prop_type = prop_type[1:-1] if prop_type else prop_type

    if not prop_type:
        prop_type = "S"
    prop.prop_type = prop_type

    comment = comment[1:] if comment else comment
    prop.name = name
    prop.unique = unique == "&"
    prop.index = name == "name" or prop.unique or qualifier == "*"
    prop.index_key = qualifier == "**"
    prop.index_text = qualifier == "***"
    prop_type = prop_type or _infer_type(default_value)
    if len(default_value) >= 2 and (
        default_value[0] == "'" and default_value[-1] == "'" or default_value[0] == '"' and default_value[-1] == '"'
    ):
        default_value = default_value[1:-1]
    prop.defaultvalue = pointer_type or default_value
    prop.type = j.data.types.get_js_type(prop_type, prop.defaultvalue)
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
    # print(f"parsing \n {text}")
    text = _normalize_string(text)
    if text.count("@url") != 1:
        raise RuntimeError("The number of urls must be equal to one.")
    lines = text.split("\n")
    schema = Schema()
    for line in lines:
        if line.startswith("@"):
            name, value = _parse_system_prop(line)
            schema.system_props[name] = value
        elif line.startswith("#") or not line.strip():
            continue
        else:
            name, prop = _parse_prop(line)
            schema.props[name] = prop
    schema.url = schema.system_props["url"]
    return schema
