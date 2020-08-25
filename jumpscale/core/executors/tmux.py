"""tmux module allows manipulation of tmux sessions, pane and launching background commands in it

"""
import libtmux
from jumpscale.core.logging import export_module_as as logger

from .command_builder import cmd_from_args

__all__ = ["execute_in_window"]

server = libtmux.Server()
JS_SESSION_NAME = "js-ng"


def create_session(session_name, kill_if_exists=False):
    return server.new_session(session_name, kill_session=kill_if_exists)


def kill_session(session_name):
    return server.kill_session(session_name)


def get_session(session_name):
    try:
        session = server.find_where({"session_name": session_name})
        if not session:
            return create_session(session_name)
    except libtmux.exc.LibTmuxException:
        return create_session(session_name)
    return session


def get_js_session():
    return get_session(JS_SESSION_NAME)


def get_js_window(window_name):
    return get_window(session_name=JS_SESSION_NAME, window_name=window_name)


def get_window(session_name, window_name):
    session = get_session(session_name)
    window = session.find_where({"window_name": window_name})
    if not window:
        window = session.new_window(window_name)
    return window


@cmd_from_args
def execute_in_window(cmd, window_name, session_name=None):
    """
    execute a command in a new tmux window

    Args:
        cmd (str or list): command as a string or an argument list, e.g. `"ls -la"` or `["ls", "la"]`
        window_name (str): window name
    """
    if session_name:
        window = get_window(session_name, window_name)
    else:
        window = get_js_window(window_name)
    window.attached_pane.send_keys(cmd)
