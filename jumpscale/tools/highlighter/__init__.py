import pygments
import pygments.formatters
import pygments.lexers
from pygments.lexers import guess_lexer



## TODO: revise code here probably we can get by guess_lexer only :)

class Lexers:
    def __init__(self):
        self._lexers = {}

    @property
    def _items(self):
        res = [item.lower().replace("lexer", "") for item in pygments.lexers.__all__ if item[0].upper() == item[0]]
        return res

    def __getattr__(self, key):
        if key.startswith("_"):
            return self.__dict__[key]
        return self.get(key)

    def get(self, key):
        key2 = key.lower().replace("lexer", "")
        if key2 not in self._lexers:
            self._lexers[key2] = pygments.lexers.get_lexer_by_name(key2)
        return self._lexers[key2]

    def __dir__(self):
        return self._items

    def __setattr__(self, key, value):
        if key.startswith("_"):
            self.__dict__[key] = value
            return
        raise j.exceptions.Base("readonly")

    def __str__(self):
        out = "Pygments lexers"
        for item in self._items:
            out += item
        return out

    __repr__ = __str__


class Formatters:
    def __init__(self):
        self._formatters = {}

    @property
    def _items(self):
        return [
            item.lower().replace("formatter", "") for item in pygments.formatters.__all__ if item[0].upper() == item[0]
        ]

    def __getattr__(self, key):
        if key.startswith("_"):
            return self.__dict__[key]
        return self.get(key)

    def get(self, key):
        key2 = key.lower().replace("formatter", "")
        if key2 not in self._formatters:
            self._formatters[key2] = pygments.formatters.get_formatter_by_name(key2)
        return self._formatters[key2]

    def __dir__(self):
        return self._items

    def __setattr__(self, key, value):
        if key.startswith("_"):
            self.__dict__[key] = value
            return
        raise j.exceptions.Base("readonly")

    def __str__(self):
        out = "Pygment Formatters:\n\n"
        for item in self._items:
            out += item
        return out

    __repr__ = __str__



lexers = Lexers()
formatters = Formatters()

def print_python(text, formatter="terminal"):
    C = text
    print(pygments.highlight(C, lexers.get("python"), formatters.get(formatter)))

def print_toml(text, formatter="terminal"):
    C = text
    print(pygments.highlight(C, lexers.get("toml"), formatters.get(formatter)))


def print_highlighted(txt, lexer=None, formatter="terminal"):
    lexer = lexer or guess_lexer(txt)
    print(pygments.highlight(txt, lexer, formatters.get(formatter)))


def test():
    C = """
    def _init(self,**kwargs):
        self.lexers = Lexers()
        self.formatters = Formatters()
        

    def print_python(self,text,formatter="terminal"):
        C=Tools.text_replace(text)
        print(pygments.highlight(C,self.lexers.get("python"), self.formatters.get(formatter)))


    """

    print_python(C)
    print_highlighted(C)

    print("####TOML EXAMPLE####")

    C = """

    title = "TOML Example"

    [owner]
    name = "Tom Preston-Werner"
    organization = "GitHub"
    bio = "GitHub Cofounder & CEO"
    dob = 1979-05-27T07:32:00Z # First class dates? Why not?

    [database]
    server = "192.168.1.1"
    ports = [ 8001, 8001, 8002 ]
    connection_max = 5000
    enabled = true
            
    """
    print_toml(C)
    print_highlighted(C)