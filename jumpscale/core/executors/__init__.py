from .local import execute as run_local
from .remote import execute as run_remote, RemoteExecutor
from .tmux import execute_in_window as run_tmux
