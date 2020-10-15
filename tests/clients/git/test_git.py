import string

from jumpscale.loader import j
from tests.base_tests import BaseTests


class GitTests(BaseTests):

    def setUp(self):
        super().setUp()
        self.instance_name = self.random_name()
        
        j.sals.process.execute("cd /tmp/ && git clone https://github.com/mhost39/test.git")
        self.git_client = j.clients.git.new(name=self.instance_name, path="/tmp/test/")

    def tearDown(self):
        j.clients.git.delete(self.instance_name)
        j.sals.fs.rmtree(path=f"/tmp/test")

    def test01_git_branch(self):
        """Test case for checking a branch name.

        **Test Scenario**
        - Get a git client.
        - Check if branch name equal main.
        """
        self.info("Check if branch name equal main")
        self.assertEqual(self.git_client.branch_name, "main")

    def test02_git_modifed_files(self):
        """Test case for checking a modifed files.

        **Test Scenario**
        - Get a git client.
        - Create a file in repository path.
        - Check if file has been modifed
        """
        self.info("Create a file in repository path")
        file_name = self.random_name()
        j.sals.fs.touch(f"/tmp/test/{file_name}")

        self.info("Check if file has been modifed")
        self.assertIn(file_name, str(self.git_client.get_modified_files()))

    def test03_git_commit(self):
        """Test case for checking a modifed files.

        **Test Scenario**
        - Get a git client.
        - Create a file in repository path.
        - Commit changes.
        - Get commit logs.
        - Check if commits has been done.
        """
        file_name = self.random_name()
        commit_msg = self.random_name()

        self.info("Create a file in repository path")
        j.sals.fs.touch(f"/tmp/test/{file_name}")

        self.info("Commit changes")
        self.git_client.commit(commit_msg)

        self.info("Get commit logs")
        last_commit = j.sals.process.execute("cd /tmp/test/ && git log -1")

        self.info("Check if commits has been done")
        self.assertIn(commit_msg, str(last_commit))

    def test04_git_pull(self):
        """Test case for pull from repository

        **Test Scenario**
        - Get a git client.
        - Delet README.md file from local repository.
        - Reset local changes.
        - Pull from remote repository.
        - Check if README.md has been pulled from remote repository.
        """
        self.info("Delet readme.dm file from local repository")
        j.sals.process.execute("rm /tmp/test/README.md")

        self.info("Reset local changes")
        j.sals.process.execute("cd /tmp/test && git reset --hard")

        self.info("Pull from remote repository")
        self.git_client.pull()

        self.info("Check if redme.dm has been pulled from remote repository")
        self.assertEqual(j.sals.fs.is_file("/tmp/test/README.md"), True)
        