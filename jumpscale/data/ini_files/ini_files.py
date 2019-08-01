file = "test.ini"


"""
class INIParser:
    def __init__(self, file_name):
        self.data = self._parse(file_name)"""


def _parse(file_directory):
    with open(file_directory, "r") as file:
        content = file.readlines()

    content_as_dict = {}
    section = ""
    for line in content:
        if line.startswith("["):
            section = ""
            section = line.strip()[1:-1]
            content_as_dict[section] = {}
        elif "=" in line:
            key, value = line.split("=")
            content_as_dict[section][key.strip()] = value.strip()
    return content_as_dict


def get_sections(file_directory):
    content = _parse(file_directory)
    sections = content.keys()
    return list(sections)


def get_properties(file_directory, section_name):
    content = _parse(file_directory)
    properties = content[section_name]
    return properties


def check_section(file_directory, section_name):
    result = section_name in get_sections(file_directory)
    return result


def check_property(file_directory, section_name, property_name):
    result = property_name in get_properties(file_directory, section_name)
    return result


def get_value(file_directory, section_name, property_name):
    content = _parse(file_directory)
    value = content[section_name][property_name]
    return value


def _write(file_directory, new_content):
    content_list = []
    for key, value in new_content.items():
        content_list.append("\n[" + key + "]")
        for key, value in value.items():
            content_list.append("\n" + key + " = " + value)
    content_text = "".join(content_list)
    with open(file_directory, "w") as file:
        file.write(content_text)


def add_section(file_directory, section_name):
    content = _parse(file_directory)
    content[section_name] = {}
    _write(file_directory, content)


def add_property(file_directory, section_name, property_key, property_value):
    content = _parse(file_directory)
    content[section_name][property_key] = property_value
    _write(file_directory, content)


def remove_section(file_directory, section_name):
    content = _parse(file_directory)
    del content[section_name]
    _write(file_directory, content)


def remove_property(file_directory, section_name, property_name):
    content = _parse(file_directory)
    del content[section_name][property_name]
    _write(file_directory, content)


remove_property(file, "test", "age")

