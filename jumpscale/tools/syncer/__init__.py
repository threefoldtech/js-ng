"""Module to help syncing multiple machines with specific directories you have.
used in the jsync tool.
```
JS-NG> xmonader = j.clients.sshkey.new("xmonader")
JS-NG> xmonader.private_key_path = "/home/xmonader/.ssh/id_rsa"
JS-NG> xmonader.load_from_file_system()
JS-NG> xmonader.save()
JS-NG> xmonader = j.clients.sshclient.new("xmonader")
JS-NG> xmonader.sshkey = "xmonader"
JS-NG> s = j.tools.syncer.Syncer(["xmonader"], {"/home/xmonader/wspace/tfchain-py":"/tmp/tfchain-py"})
JS-NG> s.start()
2019-09-03T11:38:47.183394+0200 - paths: {'/home/xmonader/wspace/tfchain-py': '/tmp/tfchain-py'}
```
"""

from jumpscale.loader import j
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer
import gevent
from typing import List, Dict, Optional

DEFAULT_IGNORED_PATTERNS = [".git", ".pyc", "__pycache__", ".swp", ".swx"]


class Syncer(PatternMatchingEventHandler):
    def __init__(
        self,
        sshclients_names: List[str],
        paths: Dict[str, str],
        patterns: Optional[List[str]] = None,
        ignore_patterns: Optional[List[str]] = None,
        ignore_directories: Optional[List[str]] = False,
        case_sensitive: bool = True,
    ):
        """Creates new syncer tool

        Arguments:
            sshclients_names {List[str]} -- list of sshclient names
            paths {Dict[str, str]} -- paths to watch src/dest form of dict {'/tmp/myproj':'/root/proj'}

        Keyword Arguments:
            patterns {Optional[List[str]]} -- optional list of patterns to watch (default: {None})
            ignore_patterns {Optional[List[str]]} -- patterns to ignore, e.g .git, __pycache__ (default: {None})
            ignore_directories {Optional[List[str]]} -- directories to ignore (default: {False})
            case_sensitive {bool} -- case sensitive watching  (default: {True})

        Returns:
            Syncer -- Syncer object
        """
        ignore_patterns = ignore_patterns or DEFAULT_IGNORED_PATTERNS
        super().__init__(patterns, ignore_patterns, ignore_directories, case_sensitive)
        self.observer = Observer()
        self.sshclients_names = sshclients_names
        self.paths = paths or {}  # src:dst

    def _get_dest_path(self, src_path: str) -> str:
        """returns destination path in remote machine

        Arguments:
            src_path {str} -- path in source machine

        Returns:
            str -- path in remote machine
        """
        j.logger.debug(f"paths: {self.paths} and path: {src_path}")

        for path in self.paths.keys():
            if path.startswith(src_path):
                return self.paths[src_path]

    def _rewrite_path_for_dest(self, src_path: str) -> str:
        """rewrite src_path to remote_path
        e.g
            local: /tmp/myproj/file.py
            remote: /root/myproj/file.py

        Arguments:
            src_path {str} -- source machine path

        Returns:
            str -- rewritten path for remote
        """
        src_path = str(src_path)
        for path in self.paths.keys():
            if src_path.startswith(path):
                return src_path.replace(path, self.paths[path])

    def _get_sshclients(self):
        """Returns list of sshclient objects.

        Returns:
            List[SSHClient] -- list of ssh clients
        """
        clients = []
        for name in self.sshclients_names:
            clients.append(j.clients.sshclient.get(name))
        return clients

    def sync(self):
        """Sync directory structure and files

        """
        j.logger.debug(f"paths: {self.paths}")

        def ensure_dirs():
            """For every directory in watched paths we make sure it's full path exists on remote.

            """
            for path in self.paths:
                for src_dir in j.sals.fs.walk_dirs(path):
                    dest_dir = str(self._rewrite_path_for_dest(src_dir))
                    for cl in self._get_sshclients():
                        j.logger.debug(f"making dir {dest_dir}")
                        cl.sshclient.run(f"mkdir -p {dest_dir}")
                        self.observer.schedule(self, src_dir)

        def sync_file(e):
            """Sync single file to all registered sshclients

            Arguments:
                e {str} -- file path
            """
            dest_path = self._rewrite_path_for_dest(e)
            j.logger.debug(f"syncing {e} to machines into {dest_path}")

            for cl in self._get_sshclients():
                cl.sshclient.run(f"mkdir -p {j.sals.fs.parent(dest_path)}")
                cl.sshclient.sftp.put(e, self._rewrite_path_for_dest(e))

        def filter_ignored(e):
            return True

        ensure_dirs()

        for path in self.paths:
            for f in j.sals.fs.walk_files(path, sync_file):
                sync_file(f)

    def start(self, sync=True):
        """Start syncing/watching paths to remote machines

        Keyword Arguments:
            sync {bool} -- sync dirs/files first (default: {True})
        """
        if sync:
            self.sync()

        for path in self.paths.keys():
            self.observer.schedule(self, path)

        self.observer.start()
        try:
            while True:
                gevent.sleep(0.1)
        except KeyboardInterrupt:
            self.observer.unschedule_all()
            self.observer.stop()
        self.observer.join()

    def on_moved(self, event):
        super().on_moved(event)

        what = "directory" if event.is_directory else "file"
        j.logger.info(f"Moved {what}: from {event.src_path} to {event.dest_path}")
        dest_path = self._rewrite_path_for_dest(event.dest_path)
        j.logger.debug(f"will move to {dest_path}")
        j.logger.debug(f"will delete original in {self._rewrite_path_for_dest(event.src_path)}")
        for cl in self._get_sshclients():
            if not event.is_directory:
                try:
                    # in case file is moved
                    cl.sshclient.sftp.put(event.dest_path, dest_path)
                    cl.sshclient.run(f"rm {self._rewrite_path_for_dest(event.src_path)}")
                except:
                    j.logger.debug(f"Ignoring {dest_path}. Path was not found during move event")
            else:
                # in case file is directory
                cl.sshclient.sftp.posix_rename(self._rewrite_path_for_dest(event.src_path), dest_path)

    def on_created(self, event):
        super().on_created(event)
        what = "directory" if event.is_directory else "file"
        j.logger.debug(f"Created {what}: {event.src_path}")

        dest_path = self._rewrite_path_for_dest(event.src_path)
        j.logger.debug(f"will create in {dest_path}")

        for cl in self._get_sshclients():
            if what == "directory":
                cl.sshclient.run(f"mkdir -p {dest_path}")
                self.observer.schedule(self, event.src_path)
            else:
                try:
                    cl.sshclient.run(f"mkdir -p {j.sals.fs.parent(dest_path)}")
                    cl.sshclient.run(f"touch {dest_path}")
                except:
                    j.logger.debug(f"Ignoring {dest_path}. Path was not found during create event")

    def on_deleted(self, event):
        super().on_deleted(event)

        what = "directory" if event.is_directory else "file"
        j.logger.debug(f"Deleted {what}: {event.src_path}")

        dest_path = self._rewrite_path_for_dest(event.src_path)
        j.logger.debug(f"will delete in {dest_path}")
        for cl in self._get_sshclients():
            if what == "directory":
                cl.sshclient.run(f"rm -rf {dest_path}")
            else:
                try:
                    cl.sshclient.run(f"rm {dest_path}")
                except:
                    j.logger.debug(f"Ignoring {dest_path}. Path was not found during delete event")

    def on_modified(self, event):
        super().on_modified(event)
        what = "directory" if event.is_directory else "file"
        j.logger.debug(f"Modified {what}: {event.src_path}")

        dest_path = self._rewrite_path_for_dest(event.src_path)
        j.logger.debug(f"will modify in {dest_path}")

        for cl in self._get_sshclients():
            if what == "directory":
                j.logger.debug(f"Folder {dest_path} was modified")
            else:
                try:
                    cl.sshclient.sftp.put(event.src_path, dest_path)
                except:
                    j.logger.debug(f"Ignoring {dest_path}. Path was not found during modify event")
