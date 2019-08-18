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
    text = text.strip()
    result = ""
    whitespaces = [" ", "\t"]
    in_comment = False
    for i, c in enumerate(text):
        if c == "#":
            in_comment = True
        if c == "\n":
            in_comment = False
        if not in_comment and c in whitespaces:
            continue
        if not in_comment and c == "\n" and text[i - 1] == "\n":
            continue
        result += c
    return result


def _correct_url_number(text):
    url_count = text.count("@url")
    return url_count == 1


def _parse_system_prop(line):
    return line[1:].split("#")[0].split("=")


def _name_in_correct_form(name):
    for c in name:
        if c != "_" and not (
            ord(c) >= ord("a")
            and ord(c) <= ord("z")
            or ord(c) >= ord("A")
            and ord(c) <= ord("Z")
            or ord(c) >= ord("0")
            and ord(c) <= ord("9")
        ):
            return False
    return (
        name[0] == "_"
        or ord(name[0]) >= ord("a")
        and ord(name[0]) <= ord("z")
        or ord(name[0]) >= ord("A")
        and ord(name[0]) <= ord("Z")
    )


def _is_int(value):
    for e in value:
        if ord(e) < ord("0") or ord(e) > ord("9"):
            return False
    return True


def _is_float(value):
    if "." not in value:
        return False
    a, b = value.split(".", 1)
    return _is_int(a) and _is_int(b)


def _infer_type(value):
    if value[0] == '"' and value[-1] == '"' or value[0] == "'" and value[-1] == "'":
        return "str"
    elif _is_float(value):
        return "float"
    elif _is_int(value):
        return "i"
    elif value == "[]":
        return "ls"
    elif value == "true" or value == "false":
        return "bool"
    else:
        raise RuntimeError(f"Can't infer the type of {value}")


def _parse_prop(line):
    prop = Property()
    if "#" in line:
        line, comment = line.split("#", 1)
        prop.comment = comment

    if line.count("=") != 1:
        raise RuntimeError("The numebr of = in one line must be exactly one")
    name, desc = line.split("=")
    prop.unique = name.startswith("&")
    prop.index_text = name.endswith("***")
    prop.index_key = not prop.index_text and name.endswith("**")
    prop.index = prop.unique or not prop.index_text and not prop.index_key and name.endswith("*")
    if name.startswith("&"):
        name = name[1:]
    if name.endswith("***"):
        name = name[:-3]
    elif name.endswith("**"):
        name = name[:-2]
    elif name.endswith("*"):
        name = name[:-1]
    if not _name_in_correct_form(name):
        raise RuntimeError("Name must consist of a sequence of digits, chars, or _ and start with a char or _")
    prop.name = name
    pointer_type = None
    if "!" in desc:
        desc, pointer_type = desc.split("!", 1)
        if "(" not in desc:
            raise RuntimeError("Type must be specified when supplying a pointer type")

    if "(" in desc:
        prop_type = desc.split("(", 1)[1].split(")", 1)[0]
        default_value = pointer_type or desc.split("(", 1)[0]
    else:
        default_value = desc
        prop_type = _infer_type(default_value)

    if prop_type == "str":
        if not (default_value[0] == '"' and default_value[-1] == '"') and not (
            default_value[0] == "'" and default_value[-1] == "'"
        ):
            raise RuntimeError("String data type must be enclosed between quotes")
        default_value = default_value[1:-1]
    prop.type = prop_type
    prop.defaultvalue = default_value
    return prop.name, prop


def parse_schema(text):
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

