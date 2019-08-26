import colorama
import getpass
import os


NAMES_TO_COLORS = {}
for attrname in dir(colorama.Fore):
    if attrname.isupper():
        NAMES_TO_COLORS[attrname] = getattr(colorama.Fore, attrname)


def format(s):
    return s.format(**NAMES_TO_COLORS)


def printcolors(s):
    """
	>>> j.tools.console.printcolors("{RED}Hello world")
	Hello world
	>>> j.tools.console.printcolors("{GREEN}Hello world")
	Hello world

	Arguments:
	s {[type]} -- [description]
	"""
    print(format(s))


def ask_password(prompt, forbidden=[], traceback=""):
    password = getpass.getpass(prompt)
    if password not in forbidden:
        return password
    else:
        raise ValueError(traceback)


def ask_yes_no(prompt, default="y", valid=["y", "n"], traceback=""):
    answer = input(prompt)
    if answer in valid:
        return answer
    elif answer == "":
        answer = default
        return answer
    else:
        raise ValueError(traceback)


def ask_int(prompt="Type int : ", traceback="", mini=None, maxi=None):
    answer = input(prompt)
    answer = int(answer)

    if mini is not None and maxi is not None:
        if mini <= answer <= maxi:
            return answer
        else:
            raise ValueError(traceback)

    elif mini is not None and maxi is None:
        if mini <= answer:
            return answer
        else:
            raise ValueError(traceback)

    elif mini is None and maxi is not None:
        if answer <= maxi:
            return answer
        else:
            raise ValueError(traceback)

    else:
        return answer


def ask_float(prompt="Type float : ", traceback="", mini=None, maxi=None):
    answer = input(prompt)
    answer = float(answer)

    if mini is not None and maxi is not None:
        if mini <= answer <= maxi:
            return answer
        else:
            raise ValueError(traceback)

    elif mini is not None and maxi is None:
        if mini <= answer:
            return answer
        else:
            raise ValueError(traceback)

    elif mini is None and maxi is not None:
        if answer <= maxi:
            return answer
        else:
            raise ValueError(traceback)

    else:
        return answer


def ask_choice(prompt="Make your choice : ", choices_list=[], traceback="We don't have that"):
    number = 0
    for choice in choices_list:
        number += 1
        print(f"{number}. " + choice)
    answer = input(prompt)

    try:
        return choices_list[int(answer) - 1]

    except ValueError:
        if answer in choices_list:
            return answer
        else:
            raise IndexError(traceback)


def ask_multi_choices(prompt="Add to choices : ", choices_list=[], traceback="Not found", tosave="s", toquit="q"):
    selected_choices = []
    print(f"'{tosave}' to save and '{toquit}' to quit")
    number = 0
    for choice in choices_list:
        number += 1
        print(f"{number}. " + choice)

    while True:
        answer = input(prompt)
        if answer == toquit:
            return []
        elif answer == tosave or answer == "":
            return selected_choices
        else:
            try:
                selected_choices.append(choices_list[int(answer) - 1])

            except ValueError:
                if answer in choices_list:
                    selected_choices.append(answer)
                else:
                    raise IndexError(traceback)


def ask_multi_lines(prompt="", escape_string="."):
    text = []
    user_input = input(prompt)
    while user_input != escape_string:
        text.append(user_input)
        user_input = input()
    return "\n".join(text)

