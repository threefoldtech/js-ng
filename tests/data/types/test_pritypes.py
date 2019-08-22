import pytest
from jumpscale.god import j


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

