'''Highlighter module helps with formatting text to be highlighted in terminal and in web

example:

```
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
```
'''
import pygments
from pygments.formatters import get_formatter_by_name
from pygments.lexers import guess_lexer, find_lexer_class_by_name


def print_highlighted(txt, lexer=None, formatter="terminal"):
    lexer = find_lexer_class_by_name(lexer) if lexer else guess_lexer(txt)
    print(pygments.highlight(txt, lexer, get_formatter_by_name(formatter)))


print_python = print_highlighted
print_toml = print_highlighted


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
