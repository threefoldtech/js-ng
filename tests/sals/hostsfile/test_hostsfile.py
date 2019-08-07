import tempfile
from jumpscale.god import j


def test_add():
    with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
        hf = j.sals.hostsfile.HostsFile(tmp.name)
        hf.add("0.0.0.0", "a")
        hf.add("0.0.0.1", "b")
        hf.add("0.0.0.2", "c")
    assert "0.0.0.0" in hf.content
    assert "0.0.0.1" in hf.content
    assert "0.0.0.2" in hf.content


def test_exists():
    with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
        hf = j.sals.hostsfile.HostsFile(tmp.name)
        hf.add("0.0.1.0", "d")
    assert hf.exists("0.0.1.0") == True
    assert hf.exists("0.0.1.1") == False


def test_remove():
    with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
        hf = j.sals.hostsfile.HostsFile(tmp.name)
        hf.add("0.0.2.0", "e")
    assert hf.remove("0.0.2.0") not in hf.content


def test_set_hostname():
    with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
        hf = j.sals.hostsfile.HostsFile(tmp.name)
        hf.set_hostname("0.0.3.0", "f")
    assert "0.0.3.0" in hf.content


def test_get_hostname():
    with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
        hf = j.sals.hostsfile.HostsFile(tmp.name)
        hf.add("0.0.4.0", "h")
    assert hf.get_hostname("0.0.4.0") == "h"
