from jumpscale.god import j
import pytest
import random
import string
import uuid


def test_random_int():

    number1 = j.data.idgenerator.random_int(0, 20)
    number2 = j.data.idgenerator.random_int(1, 30)
    number3 = j.data.idgenerator.random_int(2, 40)
    number4 = j.data.idgenerator.random_int(3, 50)
    number5 = j.data.idgenerator.random_int(4, 60)
    number6 = j.data.idgenerator.random_int(5, 70)
    number7 = j.data.idgenerator.random_int(6, 80)

    assert number1 >= 0 and number1 <= 20
    assert number2 >= 1 and number2 <= 23
    assert number3 >= 2 and number3 <= 40
    assert number4 >= 3 and number4 <= 50
    assert number5 >= 4 and number5 <= 60
    assert number6 >= 5 and number6 <= 70
    assert number7 >= 6 and number7 <= 80


def test_guid():
    parts = str.split("-")
    return len(parts) == 5 and parts[0] == 8 and parts[1] == 4 and parts[2] == 4 and parts[3] == 4 and parts[4] == 12


def test_n_from_choices():
    choices = ["a", "b", "c", "d", "e", "f"]
    str1 = j.data.idgenerator.n_from_choices(2, choices)
    str2 = j.data.idgenerator.n_from_choices(3, choices)
    str3 = j.data.idgenerator.n_from_choices(4, choices)
    str4 = j.data.idgenerator.n_from_choices(5, choices)
    assert len(str1) == 2 and str1[0] in choices and str1[1] in choices
    assert len(str2) == 3 and str2[0] in choices and str2[1] in choices and str2[2] in choices
    assert len(str3) == 4 and str3[0] in choices and str3[1] in choices and str3[2] in choices and str3[3] in choices
    assert (
        len(str4) == 5
        and str4[0] in choices
        and str4[1] in choices
        and str4[2] in choices
        and str4[3] in choices
        and str4[4] in choices
    )


def tests_chars():
    str1 = j.data.idgenerator.chars(2)
    str2 = j.data.idgenerator.chars(4)
    str3 = j.data.idgenerator.chars(6)
    str4 = j.data.idgenerator.chars(8)

    assert len(str1) == 2 
    assert len(str2) == 4  
    assert len(str3) == 6   
    assert len(str4) == 8  

def n_bytes():
     

