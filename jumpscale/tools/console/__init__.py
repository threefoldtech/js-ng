"""Console module helps with coloring in the console and asking for input from the user.
```
JS-NG> j.tools.console.printcolors("{RED}Hello{BGRED}What{WHITE}OK")                                                                     
JS-NG> j.tools.console.printcolors("{RED}Hello{BGRED}What{RESET}{WHITE}OK")                                                              
```

"""


import colorama
import getpass
import os


NAMES_TO_COLORS = {}
for attrname in dir(colorama.Fore):
    if attrname.isupper():
        NAMES_TO_COLORS[attrname] = getattr(colorama.Fore, attrname)

for attrname in dir(colorama.Back):
    if attrname.isupper():
        NAMES_TO_COLORS["BG" + attrname] = getattr(colorama.Back, attrname)

NAMES_TO_COLORS["RESET"] = colorama.Style.RESET_ALL


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


def ask_password(prompt="Password : ", forbiddens=[]):
    """Prompt the user for a password without echoing
    
    Keyword Arguments:
        prompt {str} -- the question message (default: {"Password : "})
        forbiddens {list} -- the list of bad passwords (default: {[]})
    
    Returns:
        str -- the appropriate input password
    """
    password = getpass.getpass(prompt)
    if password not in forbiddens:
        return password
    else:
        return ask_password(prompt, forbiddens)


def ask_yes_no(prompt="[y/n] :", default="y", valid=["y", "n"]):
    """Display a yes/no question and loop until a valid answer is entered
    
    Keyword Arguments:
        prompt {str} -- the question message (default: {'[y/n] :'})
        default {str} -- the default answer if there is no answer (default: {"y"})
        valid {list} -- the list of appropriate answers (default: {["y", "n"]})
    
    Returns:
        str -- the answer
    """

    answer = input(prompt)
    if answer in valid:
        return answer
    elif answer == "":
        return default
    else:
        return ask_yes_no(prompt, default, valid)


def ask_int(prompt="Type int :"):
    try:
        return int(input(prompt))
    except ValueError:
        return ask_int(prompt)


def ask_int_in_range(mini, maxi, prompt="Type int :"):
    """Get an integer response between two integer on asked question
    
    Arguments:
        mini {int} -- the minimum value for the number
        maxi {int} -- the maximum value for the number
    
    Keyword Arguments:
        prompt {str} -- the question message (default: {"Type int :"})
    
    Returns:
        int -- the input number on the range provided
    """
    try:
        answer = int(input(prompt))
        if mini <= answer <= maxi:
            return answer
        else:
            return ask_int_in_range(mini, maxi, prompt)
    except ValueError:
        return ask_int_in_range(mini, maxi, prompt)


def ask_float(prompt="Type float :"):
    try:
        return float(input(prompt))
    except ValueError:
        return ask_float(prompt)


def ask_float_in_range(mini, maxi, prompt="Type float :"):
    """Get an float response between two float on asked question
    
    Arguments:
        mini {float} -- the minimum value for the number
        maxi {float} -- the maximum value for the number
    
    Keyword Arguments:
        prompt {str} -- the question message (default: {"Type float :"})
    
    Returns:
        float -- the input number on the range provided
    """
    try:
        answer = float(input(prompt))
        if mini <= answer <= maxi:
            return answer
        else:
            return ask_float_in_range(mini, maxi, prompt)
    except ValueError:
        return ask_float_in_range(mini, maxi, prompt)


def _print_choices(choices_list):
    """Helper function : clear screen and print the choices in numbers"""
    os.system("clear")
    number = 0
    for choice in choices_list:
        number += 1
        print(f"{number}. " + choice)


def ask_choice(prompt="Type choice number : ", choices_list=[]):
    """Get an option from provided list
    
    Keyword Arguments:
        prompt {str} -- the question message (default: {"Type choice number : "})
        choices_list {list} -- the available options (default: {[]})
    
    Returns:
        str -- the chosen option
    """
    _print_choices(choices_list)
    answer = input(prompt)
    try:
        return choices_list[int(answer) - 1]
    except (IndexError, ValueError):
        return ask_choice(prompt, choices_list)


def ask_multi_choices(prompt="Add to choices : ", choices_list=[], to_save="s", to_quit="q"):
    """Collect multi choices from list
    
    Keyword Arguments:
        prompt {str} -- the question method (default: {"Add to choices : "})
        choices_list {list} -- the available options (default: {[]})
        to_save {str} -- escape and save choices (default: {"s"})
        to_quit {str} -- escape without saving (default: {"q"})
    
    Returns:
        list -- list of the selected choices
    """
    selected_choices = []
    print(f"'{to_save}' to save and '{to_quit}' to quit")
    _print_choices(choices_list)

    while True:
        answer = input(prompt)
        if answer == to_quit:
            return []
        elif answer == to_save or answer == "":
            return selected_choices
        else:
            try:
                selected_choices.append(choices_list[int(answer) - 1])
            except (IndexError, ValueError):
                return ask_multi_choices(prompt, choices_list, to_save, to_quit)


def ask_multi_lines(prompt="Type :", escape_string="."):
    """Get input from user provided multilines
    
    Keyword Arguments:
        prompt {str} -- the question message (default: {"Type :"})
        escape_string {str} -- escape character (default: {"."})
    
    Returns:
        str -- the text seperated by lines
    """
    text = []
    user_input = input(prompt)
    while user_input != escape_string:
        text.append(user_input)
        user_input = input(prompt)
    return "\n".join(text)


def ask_string(prompt="Type :"):
    """Just input function
    
    Keyword Arguments:
        prompt {str} -- the question message (default: {"Type :"})
    
    Returns:
        str -- the string input
    """
    return input(prompt)

    print(format(s))


def printobj(obj):
    from pprint import pprint

    pprint(obj)
