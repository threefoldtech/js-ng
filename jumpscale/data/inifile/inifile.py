class IniFile:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self._parse()

    def _parse(self):
        with open(self.file_path, "r") as file:
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

    def get_sections(self):
        content = self.data
        sections = content.keys()
        return list(sections)

    def get_properties(self, section_name):
        content = self.data
        properties = content[section_name]
        return properties

    def check_section(self, section_name):
        result = section_name in self.get_sections()
        return result

    def check_property(self, section_name, property_name):
        result = property_name in self.get_properties(section_name)
        return result

    def get_value(self, section_name, property_name):
        content = self.data
        value = content[section_name][property_name]
        return value

    def _write(self, new_content):
        content_list = []
        for key, value in new_content.items():
            content_list.append("\n[" + key + "]")
            for key, value in value.items():
                content_list.append("\n" + key + " = " + value)
        content_text = "".join(content_list)
        with open(self.file_path, "w") as file:
            file.write(content_text)

    def add_section(self, section_name):
        content = self.data
        content[section_name] = {}
        self._write(content)

    def add_property(self, section_name, property_key, property_value):
        content = self.data
        content[section_name][property_key] = property_value
        self._write(content)

    def remove_section(self, section_name):
        content = self.data
        del content[section_name]
        self._write(content)

    def remove_property(self, section_name, property_name):
        content = self.data
        del content[section_name][property_name]
        self._write(content)

