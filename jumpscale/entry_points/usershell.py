import os
import re
import time
import sys
import traceback

import inspect
import cgi

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completion
from prompt_toolkit.shortcuts import print_formatted_text
from prompt_toolkit.eventloop.async_generator import AsyncGeneratorItem
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
from jumpscale import threesdk


BASE_CONFIG_DIR = os.path.join(os.environ.get("HOME", "/root"), ".jsng")
HISTORY_FILENAME = os.path.join(BASE_CONFIG_DIR, "history.txt")

DEFAULT_TOOLBAR_MSG = "Welcome to 3sdk enter info for help"

style = Style.from_dict(
    {
        # User input (default text).
        "bottom-toolbar": "#ffffff bg:#333333",
        "default": "#aaaaaa",
        # Prompt.
    }
)


def print_error(error):
    print_formatted_text(
        HTML("<ansired>{}</ansired>".format(cgi.html.escape(str(error))))
    )


def noexpert_error(error):
    reports_location = (
        f"{os.environ.get('HOME', os.environ.get('USERPROFILE', ''))}/sandbox/reports"
    )
    error_file_location = (
        f"{reports_location}/jsxreport_{time.strftime('%d%H%M%S')}.log"
    )
    if not os.path.exists(reports_location):
        os.makedirs(reports_location)
    with open(error_file_location, "w") as f:
        f.write(str(error))
    err_msg = f"""Something went wrong. Please contact support at https://support.grid.tf/
Error report file has been created on your machine in this location: {error_file_location}
        """
    return err_msg


class Shell(Validator):
    def __init__(self):
        self._prompt = PromptSession()
        self.mode = None
        self.toolbarmsg = DEFAULT_TOOLBAR_MSG

    def get_completions_async(self, document, complete_event):
        text = document.current_line_before_cursor
        root, *more = text.split(" ")
        items = []
        if not more:
            style = "bg:ansibrightblue"
            items += threesdk.__all__
            self.toolbarmsg = DEFAULT_TOOLBAR_MSG
        else:
            style = "bg:ansigreen"
            obj = getattr(threesdk, root, None)
            if not obj:
                return
            if not hasattr(obj, more[0]):
                # complete object attributes
                self.toolbarmsg = obj.__doc__.strip().splitlines()[0]
                for name, member in inspect.getmembers(obj, inspect.isroutine):
                    if not name.startswith("_"):
                        items.append(name)
            else:
                # complete arguments
                func = getattr(obj, more[0])
                self.toolbarmsg = func.__doc__.strip().splitlines()[0]
                style = "bg:ansired"
                for arg in inspect.getfullargspec(func).args:
                    field = arg + "="
                    if field in text:
                        continue
                    items.append(field)
            text = more[-1]

        for item in items:
            if not item:
                continue
            if isinstance(item, Completion):
                item.start_position = -len(text)
            else:
                item = Completion(item, -len(text))
            regex = ".*".join(text)
            item.style = style
            if re.search(regex, item.text):
                yield AsyncGeneratorItem(item)

    def bottom_toolbar(self):
        return [("class:bottom-toolbar", self.toolbarmsg)]

    def validate(self, document):
        text = document.current_line_before_cursor
        if not text:
            return
        root, *more = text.split(" ")
        submodule = getattr(threesdk, root, None)
        if not submodule:
            raise ValidationError(message=f"No such subcommand {root}")
        if not more and callable(submodule):
            func = root
        elif more:
            func = getattr(submodule, more[0], None)
            if not func:
                raise ValidationError(message=f"{root} has no command called {more[0]}")
        else:
            raise ValidationError(message="Invalid command")
        # TODO: validate args
        return

    def get_func_kwargs(self, cmd):
        root, *extra = cmd.split()
        module = getattr(threesdk, root)
        if inspect.isroutine(module):
            return module, self.get_kwargs(*extra)
        else:
            func = getattr(module, extra[0])
            return func, self.get_kwargs(*extra[1:])

    def get_kwargs(self, *args):
        kwargs = {}
        for arg in args:
            key, val = arg.split("=", 1)
            kwargs[key] = val
        return kwargs

    def execute(self, cmd):
        try:
            func, kwargs = self.get_func_kwargs(cmd)
            func(**kwargs)
        except Exception:
            # print_error(noexpert_error(traceback.format_exc()))
            print_error(traceback.format_exc())

    def make_prompt(self):
        root = ("class:default", "3sdk>")
        while True:
            try:
                result = self.prompt([root])
                self.execute(result)
            except EOFError:
                sys.exit(0)

    def prompt(self, msg):
        return self._prompt.prompt(
            msg,
            completer=self,
            validator=self,
            style=style,
            bottom_toolbar=self.bottom_toolbar,
        )


def run():
    shell = Shell()
    shell.make_prompt()


if __name__ == "__main__":
    run()
