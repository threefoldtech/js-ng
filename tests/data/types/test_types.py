import pytest
from jumpscale.loader import j


def test_string_check():
    s = j.data.types.String()
    assert s.check("test")
    assert not s.check(45)


def test_integer_check():
    i = j.data.types.Integer()
    assert i.check("15")
    assert not i.check("hi")


def test_integer_from_str():
    i = j.data.types.Integer()
    assert i.from_str("10") == 10
    assert i.from_str("not int") == None


def test_boolean_check():
    b = j.data.types.Boolean()
    assert b.check("False")
    assert not b.check("no")


def test_boolean_from_str():
    b = j.data.types.Boolean()
    assert b.from_str("True") == True
    assert b.from_str("False") == False
    assert b.from_str("any thing else") == None


def test_float_check():
    f = j.data.types.Float()
    assert f.check("1.2")
    assert not f.check("not")


def test_float_from_str():
    f = j.data.types.Float()
    assert f.from_str("3.14") == 3.14
    assert f.from_str("not float") == None


def test_email_check():
    e = j.data.types.Email()
    assert e.check("name@example.com")
    assert e.check("oa3@gmail.com")
    assert e.check("o_a_15@gmail.com")
    assert not e.check("test.com")
    assert not e.check("me@cs")
    assert not e.check("anothername@example")


def test_path_check():
    p = j.data.types.Path()
    assert p.check("/home/me")
    assert p.check("/../../hi")
    assert p.check("/../hi")
    assert p.check("/..")
    assert not p.check("not path")


def test_url_check():
    u = j.data.types.URL()
    assert u.check("https://www.google.com")
    assert u.check("http://fb.com")
    assert u.check("http://255.255.255.255")
    assert not u.check("www.google")


def test_ip_check():
    ip = j.data.types.IPAddress()
    assert ip.check("185.145.45.5")
    assert not ip.check("44.54.5")


def test_tel_check():
    tel = j.data.types.Tel()
    assert tel.check("010055471466")
    assert tel.check("(+20) 100 48 5555")
    assert not tel.check("0200/46")


def test_datetime_check():
    dt = j.data.types.DateTime()
    assert dt.check("2003-12-31 23:59")
    assert not dt.check("2003/12/31 12:50")


def test_data_check():
    d = j.data.types.Date()
    assert d.check("2003-12-31")
    assert not d.check("2003/12/31")


def test_time_check():
    t = j.data.types.Time()
    assert t.check("23:59")
    assert not t.check("50:59")


def test_duration_check():
    d = j.data.types.Duration()
    assert d.check("22y 11m 4d")
    assert d.check("4d 22h 12m")
