import os
import re
import time
import sys
import traceback
import argparse
import requests

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
from jumpscale.threesdk import settings
from jumpscale.core.exceptions.exceptions import JSException
from jumpscale.clients.docker.docker import DockerClient
from jumpscale.threesdk.threebot import ThreeBot, DEFAULT_IMAGE
from jumpscale.core.config import get_current_version


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


def get_binary_link():
    resp = requests.get("https://api.github.com/repos/threefoldtech/js-ng/releases/latest")
    resp = resp.json()
    # get versions
    download_link = ""
    version = resp["tag_name"]
    for platform in resp["assets"]:
        if sys.platform in platform["name"]:
            download_link = platform["browser_download_url"]
    return version, download_link


def update():
    print("checking for updates")
    latest_version, binary_link = get_binary_link()
    current_version = get_current_version()
    if latest_version != current_version:
        print(f"version: {latest_version} is available get it from {binary_link}")
        return
    docker_client = DockerClient()
    print("Checking for new docker image")
    docker_client.client.images.pull(f"{DEFAULT_IMAGE}:{latest_version}")
    print("Starting 3sdk containers")
    for container_name in os.listdir(os.path.expanduser("~/.config/jumpscale/containers")):
        ThreeBot.delete(container_name)
        ThreeBot.install(container_name)


def print_error(error):
    print_formatted_text(HTML("<ansired>{}</ansired>".format(cgi.html.escape(str(error)))))


def partition_line(line):
    def replacer(m):
        return m.group().replace(" ", "\0").strip("\"'")

    result = re.sub(r"""(['"]).*?\1""", replacer, line)
    parts = []
    for part in result.split():
        parts.append(part.replace("\0", " "))
    return parts


def noexpert_error(error):
    reports_location = f"{os.environ.get('HOME', os.environ.get('USERPROFILE', ''))}/sandbox/reports"
    error_file_location = f"{reports_location}/jsngreport_{time.strftime('%d%H%M%S')}.log"
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
        parts = partition_line(text)
        if not parts:
            root = None
            more = []
        else:
            root, more = parts[0], parts[1:]
        items = []
        if not root or not hasattr(threesdk, root):
            style = "bg:ansibrightblue"
            items += threesdk.__all__
            self.toolbarmsg = DEFAULT_TOOLBAR_MSG
        else:
            style = "bg:ansigreen"
            obj = getattr(threesdk, root)
            if not more or not hasattr(obj, more[0]):
                # complete object attributes
                self.toolbarmsg = threesdk._get_doc_line(obj.__doc__)
                for name, member in inspect.getmembers(obj, inspect.isroutine):
                    if not name.startswith("_"):
                        items.append(name)
                text = "" if not more else more[-1]
            else:
                # complete arguments
                func = getattr(obj, more[0])
                self.toolbarmsg = threesdk._get_doc_line(func.__doc__)
                style = "bg:ansired"
                for arg in inspect.getfullargspec(func).args:
                    field = arg + "="
                    if field in text:
                        continue
                    items.append(field)
                if len(more) > 1:
                    text = more[-1]
                else:
                    text = ""

        for item in items:
            if not item:
                continue
            if isinstance(item, Completion):
                item.start_position = -len(text)
            else:
                item = Completion(item, -len(text))
            regex = ".*".join(text)
            item.style = style
            if not text or re.search(regex, item.text):
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
        parts = partition_line(cmd)
        root, extra = parts[0], parts[1:]
        module = getattr(threesdk, root)
        if inspect.isroutine(module):
            return module, self.get_kwargs(module, *extra)
        else:
            func = getattr(module, extra[0])
            return func, self.get_kwargs(func, *extra[1:])

    def get_kwargs(self, func, *args):
        funcspec = inspect.getfullargspec(func)
        kwargs = {}
        for arg in args:
            key, val = arg.split("=", 1)
            isbool = funcspec.annotations.get(key) is bool
            if isbool:
                if val:
                    val = val.lower() in ["y", "yes", "1", "true"]
                else:
                    val = True
            kwargs[key] = val
        return kwargs

    def execute(self, cmd):
        if not cmd.strip():
            return
        try:
            func, kwargs = self.get_func_kwargs(cmd)
            func(**kwargs)
        except JSException as e:
            if not settings.expert:
                print_error(str(e))
            else:
                print_error(traceback.format_exc())
        except Exception:
            if not settings.expert:
                print_error(noexpert_error(traceback.format_exc()))
            else:
                print_error(traceback.format_exc())

    def make_prompt(self):
        root = ("class:default", "3sdk>")
        while True:
            try:
                result = self.prompt([root])
                self.execute(result)
            except (EOFError, KeyboardInterrupt):
                sys.exit(0)

    def prompt(self, msg):
        return self._prompt.prompt(
            msg, completer=self, validator=self, style=style, bottom_toolbar=self.bottom_toolbar,
        )


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--update", action="store_true", help="Update 3sdk")
    parser.add_argument("--expert", action="store_true", help="Run 3sdk in expert mode")
    args = parser.parse_args()
    settings.expert = args.expert

    if args.update:
        update()
    else:
        shell = Shell()
        shell.make_prompt()


if __name__ == "__main__":
    run()
