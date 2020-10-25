import git
from jumpscale.clients.base import Client
from jumpscale.core.base import fields
from jumpscale.loader import j


class GitClient(Client):
    path = fields.String()

    def __init__(self):
        super().__init__()
        self.__repo = None

    @property
    def repo(self):
        if not self.__repo:
            self.__repo = git.Repo(self.path)
        return self.__repo

    def set_remote_url(self, url, remote_name="origin"):
        remote = self.repo.remote(remote_name)
        remote.set_url(url)

    @property
    def remote_url(self):
        return self.repo.remote().url

    @property
    def branch_name(self):
        return self.repo.active_branch.name

    def get_modified_files(self):
        """returns local changes in the repo

        Returns:
            dict: dict containing different types of changes(check git status man)
        """
        modified_files = self.repo.git.status(porcelain=True).splitlines()
        result_format = {}
        for mod_file in modified_files:
            if "??" in mod_file:
                continue
            state, file_name = mod_file.split()
            result_format.setdefault(state, [])
            result_format[state].append(file_name)
        untracked_files = self.repo.untracked_files
        if untracked_files:
            result_format["N"] = untracked_files
        return result_format

    def pull(self):
        """Pulls from origin

        Raises:
            j.exceptions.Input: if there is locaal changes
        """
        if self.get_modified_files():
            raise j.exceptions.Input(message="Cannot pull:{}, files waiting to commit".format(self.path))
        self.repo.git.pull()

    def commit(self, message, add_all=True):
        """adds a commit

        Args:
            message (str): commit message
            add_all (bool, optional): will add all changes before commiting. Defaults to True.

        Returns:
            [type]: [description]
        """
        if add_all and self.get_modified_files():
            self.repo.git.add("-A")
        if self.repo.index.diff("HEAD"):
            return self.repo.index.commit(message)
