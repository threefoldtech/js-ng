import libtmux
from jumpscale.god import j

__all__ = ['execute_in_window']

server = libtmux.Server()
JS_SESSION_NAME = "js-ng"
JS_WINDOW_NAME = "js-ng-w"


def create_session(session_name, kill_if_exists=False):
    return server.new_session(session_name, kill_session=kill_if_exists)


def get_session(session_name, create_if_not_existing=False):
    try:
        session = server.find_where({"session_name": session_name})
        if not session and create_if_not_existing:
            return create_session(session_name=session_name)
    except:
        j.logger.error("tmux isn't running")
        if create_if_not_existing:
            j.logger.info('Gonna start session with {} name'.format(session_name))
            return create_session(session_name=session_name)


def create_window(session_name, window_name):
    session = get_session(session_name, create_if_not_existing=True)
    return session.new_window(window_name)


def get_window(session_name, window_name, create_if_not_existing=False):
    session = get_session(session_name, create_if_not_existing=True)
    window = session.find_where({"window_name": window_name})
    if not window and create_if_not_existing:
        window = create_window(session_name, window_name)
    return window


def execute_in_window(session_name, window_name, cmd):
    window = get_window(session_name, window_name, create_if_not_existing=True)
    window.attached_pane.send_keys(cmd)


def create_js_session(kill_if_exists=False):
    return create_session(session_name=JS_SESSION_NAME, kill_if_exists=kill_if_exists)


def get_js_session():
    return get_session(session_name=JS_SESSION_NAME, create_if_not_existing=True)


def get_js_window():
    return get_window(session_name=JS_WINDOW_NAME, window_name=JS_WINDOW_NAME, create_if_not_existing=True)

def execute_in_js_window(cmd):
    execute_in_window(session_name=JS_SESSION_NAME, window_name=JS_WINDOW_NAME, cmd=cmd)
