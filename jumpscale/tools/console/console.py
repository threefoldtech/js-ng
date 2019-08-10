import colorama

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