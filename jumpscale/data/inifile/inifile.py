from configparser import ConfigParser


class IniFile:
    """
    the IniFile object parses the content of the file provided by the path argument
    Args:
        path (str) : the path to file.ini
    """

    def __init__(self, path):
        self.path = path
        self.parser = ConfigParser()
        self.parser.read(self.path)

    def write(self):
        """
        apply all the changes to the file
        """
        with open(self.path, "w") as file:
            self.parser.write(file)

    def get_sections(self):
        """
        search the file for sections names
        Returns:
            a list of the sections
        """
        return self.parser.sections()

    def get_properties(self, section_name):
        """
        get the properties name under the provided section
        Args:
            section_name (str) : the section name which contains the properties
        Returns:
            list of all the properties under the section
        """
        return self.parser.options(section_name)

    def check_section(self, section_name):
        """
        check the existence of the section
        Args:
            section_name (str) : the section wanted to check
        Returns:
            boolen expresion
        """
        return section_name in self.parser.sections()

    def check_property(self, section_name, property_name):
        """
        check the existence of the property in section
        Args:
            section_name (str) : the name of the section where the property is
            property_name (str) : the property wanted to check
        Returns:
            boolen expresion
        """
        return property_name in self.parser.options(section_name)

    def get_value(self, section_name, property_name):
        """
        gat the value of property as string
        Args:
            section_name (str) : the name of the section where the property is
            property_name (str) : the property wanted to get its value
        Returns:
            string of the value
        """
        return self.parser.get(section_name, property_name)

    def get_int(self, section_name, property_name):
        """
        gat the value of property as int
        Args:
            section_name (str) : the name of the section where the property is
            property_name (str) : the property wanted to get its value
        Returns:
            int of the value
        """
        return self.parser.getint(section_name, property_name)

    def get_float(self, section_name, property_name):
        """
        gat the value of property as float
        Args:
            section_name (str) : the name of the section where the property is
            property_name (str) : the property wanted to get its value
        Returns:
            float of the value
        """
        return self.parser.getfloat(section_name, property_name)

    def get_boolen(self, section_name, property_name):
        """
        gat the value of property as boolen
        Args:
            section_name (str) : the name of the section where the property is
            property_name (str) : the property wanted to get its value
        Returns:
            boolen of the value
        """
        return self.parser.getboolean(section_name, property_name)

    def add_section(self, section_name):
        """
        add an empty section to the file
        Args:
            section_name (str) : the section name
        """
        self.parser[section_name] = {}

    def add_property(self, section_name, property_key, property_value):
        """
        add new property to the file
        Args:
            section_name (str) : the section name
            property_key (str) : the name of the property
            property_value (str) : the value of the property
        """
        self.parser[section_name] = {property_key: property_value}

    def remove_section(self, section_name):
        """
        delete a section and its properties
        Args:
            section_name (str) : the section name
        """
        self.parser.remove_section(section_name)

    def remove_property(self, section_name, property_name):
        """
        delete a property from section
        Args:
            section_name (str) : the section name
            property_key (str) : the name of the property
        """
        self.parser.remove_option(section_name, property_name)

