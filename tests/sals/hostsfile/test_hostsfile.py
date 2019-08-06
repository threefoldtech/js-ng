from jumpscale.god import j
import pytest

hf = j.sals.hostsfile.HostsFile("sample.txt")


def test_add():
    hf.add("0.0.0.0", "a")
    hf.add("0.0.0.1", "b")
    hf.add("0.0.0.2", "c")
    assert "0.0.0.0" in hf.content
    assert "0.0.0.1" in hf.content
    assert "0.0.0.2" in hf.content


def test_exists():
    hf.add("0.0.1.0", "d")
    assert hf.exists("0.0.1.0") == True
    assert hf.exists("0.0.1.1") == False


def test_remove():
    hf.add("0.0.2.0", "e")
    assert hf.remove("0.0.2.0") not in hf.content


def test_set_hostname():
    hf.set_hostname("0.0.3.0", "f")
    assert "0.0.3.0" in hf.content


def test_get_hostname():
    hf.add("0.0.4.0", "h")
    assert hf.get_hostname("0.0.4.0") == "h"
