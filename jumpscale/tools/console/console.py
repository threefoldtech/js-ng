import colorama
import getpass


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


def ask_int(prompt, traceback="", mini=None, maxi=None):
    answer = input(prompt)
    # answer = int(answer)
    return answer

