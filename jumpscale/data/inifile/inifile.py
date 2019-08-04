from configparser import ConfigParser


class IniFile(ConfigParser):
    def __init__(self, path):
        self.path = path
        self.parser = ConfigParser()
        self.parser.read(self.path)

    def _write(self):
        with open(self.path, "w") as file:
            self.parser.write(file)

    def get_sections(self):
        return self.parser.sections()

    def get_properties(self, section_name):
        return self.parser.options(section_name)

    def check_section(self, section_name):
        return section_name in self.parser.sections()

    def check_property(self, section_name, property_name):
        return property_name in self.parser.options(section_name)

    def get_value(self, section_name, property_name):
        return self.parser.get(section_name, property_name)

    def get_int(self, section_name, property_name):
        return self.parser.getint(section_name, property_name)

    def get_float(self, section_name, property_name):
        return self.parser.getfloat(section_name, property_name)

    def get_boolen(self, section_name, property_name):
        return self.parser.getboolean(section_name, property_name)

    def add_section(self, section_name):
        self.parser[section_name] = {}
        self._write()

    def add_property(self, section_name, property_key, property_value):
        self.parser[section_name] = {property_key: property_value}
        self._write()

    def remove_section(self, section_name):
        self.parser.remove_section(section_name)
        self._write()

    def remove_property(self, section_name, property_name):
        self.parser.remove_option(section_name, property_name)
        self._write()

