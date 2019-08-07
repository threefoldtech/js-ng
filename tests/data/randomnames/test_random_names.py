from jumpscale.god import j
import pytest

# a name is composed of two non-empty parts
# separated by an underscore.
# The two parts consists only of
# lowercase english letters.


def test_generate_random_name():
    name1 = j.data.randomnames.generate_random_name()
    name2 = j.data.randomnames.generate_random_name()
    name3 = j.data.randomnames.generate_random_name()
    name4 = j.data.randomnames.generate_random_name()
    assert well_formed_name(name1)
    assert well_formed_name(name2)
    assert well_formed_name(name3)
    assert well_formed_name(name4)
    return name1 != name2 or name2 != name3 or name3 != name4


def well_formed_name(name):
    parts = name.split("_")
    return (
        len(parts) == 2
        and parts[0] != ""
        and parts[1] != ""
        and only_english_lowercase_letters(parts[0])
        and only_english_lowercase_letters(parts[1])
    )


def only_english_lowercase_letters(name):
    for l in name:
        num = ord(l)
        if num < ord("a") or num > ord("z"):
            return False
    return True
