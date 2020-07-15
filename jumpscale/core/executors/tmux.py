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


def get_js_session():
    try:
        s = server.find_where({"session_name": JS_SESSION_NAME})
        if not s:
            return create_session(JS_SESSION_NAME)
    except libtmux.exc.LibTmuxException:
        return create_session(JS_SESSION_NAME)
    return s


def get_js_window(window_name):
    s = get_js_session()
    w = s.find_where({"window_name": window_name})
    if not w:
        w = s.new_window(window_name)
        w.rename_window(window_name)

    return w


def get_window(window_name):
    w = server.find_where({"window_name": window_name})
    if not w:
        w = get_js_window(window_name)
    return w


@cmd_from_args
def execute_in_window(cmd, window_name):
    """
    execute a command in a new tmux window

    Args:
        cmd (str or list): command as a string or an argument list, e.g. `"ls -la"` or `["ls", "la"]`
        window_name (str): window name
    """
    try:
        server.list_sessions()
    except:
        logger().error("tmux isn't running")
        server.new_session(JS_SESSION_NAME)
    w = get_window(window_name)
    w.attached_pane.send_keys(cmd)
