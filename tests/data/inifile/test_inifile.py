import tempfile

from jumpscale.god import j


tmp = tempfile.NamedTemporaryFile(suffix=".ini")

foo = j.data.inifile.IniFile(tmp.name)


def read(sample_path):
    with open(sample_path, "r") as sample:
        content = sample.read()
    return content


def test_add_section():
    foo.add_section("Author")
    foo.write()
    assert "Author" in read(tmp.name)


def test_add_property():
    foo.add_property("Author", "name", "Omar")
    foo.write()
    assert "name = Omar" in read(tmp.name)


def test_remove_section():
    foo.add_section("Author")
    foo.write()
    foo.remove_section("Author")
    foo.write()
    assert "Author" not in read(tmp.name)


def test_remove_property():
    foo.add_property("Author", "name", "Omar")
    foo.write()
    foo.remove_property("Author", "name")
    foo.write()
    assert "name" not in read(tmp.name)


def test_get_sections():
    foo.add_property("Author", "name", "Omar")
    foo.add_property("App", "version", "0.1")
    foo.write()
    assert "Author" in foo.get_sections()
    assert "App" in foo.get_sections()


def test_get_properties():
    foo.add_property("Author", "name", "Omar")
    foo.write()
    assert "name" in foo.get_properties("Author")


def test_check_section():
    foo.add_property("Author", "name", "Omar")
    foo.write()
    assert foo.check_section("Author")


def test_check_property():
    foo.add_property("Author", "name", "Omar")
    foo.write()
    assert foo.check_property("Author", "name")


def test_get_value():
    foo.add_property("Author", "name", "Omar")
    foo.write()
    assert foo.get_value("Author", "name") == "Omar"


def test_get_int():
    foo.add_property("Author", "age", "22")
    foo.write()
    assert foo.get_int("Author", "age") == 22


def test_get_float():
    foo.add_property("Author", "age", "22.5")
    foo.write()
    assert foo.get_float("Author", "age") == 22.5


def test_get_boolen():
    foo.add_property("Licence", "access", "True")
    foo.write()
    assert foo.get_boolen("Licence", "access")

