from jumpscale.god import j
from watchdog.events import FileSystemEventHandler, PatternMatchingEventHandler
from watchdog.observers import Observer
import gevent

DEFAULT_IGNORED_PATTERNS = [".git", ".pyc", '__pycache__', ".swp", '.swx']

class Syncer(PatternMatchingEventHandler):

    def __init__(self, sshclients_names, paths=None, patterns=None, ignore_patterns=None, ignore_directories=False, case_sensitive=False):
        ignore_patterns = ignore_patterns or DEFAULT_IGNORED_PATTERNS
        super().__init__(patterns, ignore_patterns, ignore_directories, case_sensitive)
        self.observer = Observer()
        self.sshclients_names = sshclients_names
        self.paths = paths or {} # src:dst

    def _get_dest_path(self, src_path):
        print("paths: {} and path: {}".format(self.paths, src_path))

        for path in self.paths.keys():
            if path.startswith(src_path):
                return self.paths[src_path]
    
    def _rewrite_path_for_dest(self, src_path):
        print("paths: {} and path: {}".format(self.paths, src_path))
        src_path = str(src_path)
        for path in self.paths.keys():
            if src_path.startswith(path):
                return src_path.replace(path, self.paths[path])
    
    def _get_sshclients(self):
        clients = []
        for name in self.sshclients_names:
            clients.append(j.clients.sshclient.get(name))
        return clients
    
    def _sync(self):
        def ensure_dirs():
            for path in self.paths:
                for d in j.sals.fs.walk_dirs(path):
                    dest_d = str(self._rewrite_path_for_dest(d))
                    for cl in self._get_sshclients():
                        cl.run("mkdir -p {}".format(dest_d))


        def sync_file(e):
            entry_as_str = str(e)
            dest_path = self._rewrite_path_for_dest(entry_as_str)
            print("syncing {} to machines into {}".format(e, dest_path))

            for cl in self._get_sshclients():
                cl.run("mkdir -p {}".format(j.sals.fs.parent(dest_path)))
                cl.sftp.put(entry_as_str, self._rewrite_path_for_dest(entry_as_str))

        def filter_ignored(e):
            # EVERYTHING FOR NOW
            return True

        ensure_dirs()

        for path in self.paths:
            for f in j.sals.fs.walk_files(path, sync_file):
                pass
            
    def start(self):
        self._sync()
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

        what = 'directory' if event.is_directory else 'file'
        j.logger.info("Moved {}: from {} to {}".format(what, event.src_path,event.dest_path))
        dest_path = self._rewrite_path_for_dest(event.dest_path)
        print("will move to {}".format(dest_path))
        print("will delete original in {}".format(self._rewrite_path_for_dest(event.src_path)))
        for cl in self._get_sshclients():
            if j.sals.fs.is_file(dest_path):
                cl.sftp.mkdir(j.sals.fs.parent(dest_path), ignore_existing=True)
            else:
                cl.sftp.mkdir(dest_path, ignore_existing=True)
                
            cl.sftp.put(event.dest_path, dest_path)
            cl.run("rm {}".format(event.src_path))


    def on_created(self, event):
        super().on_created(event)
        what = 'directory' if event.is_directory else 'file'
        j.logger.info("Created {}: {}".format(what, event.src_path))

        dest_path = self._rewrite_path_for_dest(event.src_path)
        print("will create in {}".format(dest_path))
        for cl in self._get_sshclients():
            cl.sftp.mkdir(j.sals.fs.parent(dest_path), ignore_existing=True)

            cl.run("touch {}".format(dest_path))



    def on_deleted(self, event):
        super().on_deleted(event)

        what = 'directory' if event.is_directory else 'file'
        j.logger.info("Deleted {}: {}".format(what, event.src_path))

        dest_path = self._rewrite_path_for_dest(event.src_path)
        print("will delete in {}".format(dest_path))
        for cl in self._get_sshclients():
            cl.run("rm {}".format(event.src_path))

    def on_modified(self, event):
        super().on_modified(event)
        what = 'directory' if event.is_directory else 'file'
        j.logger.info("Modified {}: {}".format(what, event.src_path))

        dest_path = self._rewrite_path_for_dest(event.src_path)
        print("will modify in {}".format(dest_path))
