from hostsfile import HostsFile
import pytest

hf = HostsFile("sample.txt")


def test_add():
    hf.add("127.0.0.1", "me.com")
    hf.add("257.54.57.1", "what?")
    hf.add("485.415.4.4", "why?")
    with open("sample.txt", "r") as file:
        content = file.read()
    assert "127.0.0.1\tme.com" in content
    assert "257.54.57.1\twhat?" in content
    assert "485.415.4.4\twhy?" in content


def test_exists():
    assert hf.exists("127.0.0.1") == True
    assert hf.exists("127.3.0.1") == False


def test_remove():
    hf.remove("485.415.4.4")
    with open("sample.txt", "r") as file:
        content = file.read()
    assert "485.415.4.4" not in content


def test_set_hostname():
    hf.set_hostname("127.0.0.1", "hi")
    with open("sample.txt", "r") as file:
        content = file.read()
    assert "127.0.0.1\thi" in content


def test_get_hostname():
    hf.add("13.0.0.1", "here!")
    assert hf.get_hostname("13.0.0.1") == "here!"
    assert hf.get_hostname("159.0.0.4") == "ip does not exist"
