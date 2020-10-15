import string

from jumpscale.loader import j
from tests.base_tests import BaseTests


class GitTests(BaseTests):
    def setUp(self):
        super().setUp()
        self.instance_name = self.random_name()
        self.repo_dir = self.random_name()
        self.repo_url = "https://github.com/tfttesting/test.git"
        j.sals.fs.mkdir(f"/tmp/{self.repo_dir}")
        j.sals.process.execute(f"git clone {self.repo_url}", cwd=f"/tmp/{self.repo_dir}")
        self.git_client = j.clients.git.new(name=self.instance_name, path=f"/tmp/{self.repo_dir}/test/")

    def tearDown(self):
        j.clients.git.delete(self.instance_name)
        j.sals.fs.rmtree(path=f"/tmp/{self.repo_dir}")

    def random_name(self):
        return j.data.idgenerator.nfromchoices(10, string.ascii_letters)

    def test01_check_git_config(self):
        """Test case for checking git config file.

        **Test Scenario**
        - Get a git client.
        - Read the git.config file.
        - Check that remote_url equal to repo_url.
        - Check that url equal to remote_url.
        """
        self.info("Read the git.config file")
        git_config = j.sals.fs.read_file(f"/tmp/{self.repo_dir}/test/.git/config")

        self.info("Check that remote_url equal to repo_url")
        self.assertEqual(self.repo_url, self.git_client.remote_url)

        self.info("Check that git config url equal to remote_url")
        self.assertIn(self.git_client.remote_url, git_config)

    def test02_git_branch(self):
        """Test case for checking a branch name.

        **Test Scenario**
        - Get a git client.
        - Check if branch name equal main.
        """
        self.info("Check if branch name equal main")
        self.assertEqual(self.git_client.branch_name, "main")

    def test03_git_modifed_files(self):
        """Test case for checking a modifed files.

        **Test Scenario**
        - Get a git client.
        - Create a file in repository path.
        - Commit changes
        - modify this file
        - Check if file has been modifed
        """
        self.info("Create a file in repository path")
        file_name = self.random_name()
        j.sals.fs.touch(f"/tmp/{self.repo_dir}/test/{file_name}")

        self.info("Commit changes")
        self.git_client.commit(f"add {file_name}")

        self.info("modify this file")
        j.sals.fs.write_file(f"/tmp/{self.repo_dir}/test/{file_name}", "test modify file")

        self.info("Check if file has been modifed")
        modided_file = self.git_client.get_modified_files()["M"][0]
        self.assertEqual(file_name, modided_file)

    def test04_git_add_new_file(self):
        """Test case for checking add a new file.

        **Test Scenario**
        - Get a git client.
        - Create a file in repository path.
        - Check if a new file has been added
        """
        self.info("Create a file in repository path")
        file_name = self.random_name()
        j.sals.fs.touch(f"/tmp/{self.repo_dir}/test/{file_name}")

        self.info("Check if a new file has been added")
        added_file = self.git_client.get_modified_files()["N"][0]
        self.assertEqual(file_name, added_file)

    def test05_git_commit(self):
        """Test case for checking a commit.

        **Test Scenario**
        - Get a git client.
        - Create a file in repository path.
        - Commit the change of creating a new file.
        - Get commit logs.
        - Check if commit has been done.
        """
        file_name = self.random_name()
        commit_msg = self.random_name()

        self.info("Create a file in repository path")
        j.sals.fs.touch(f"/tmp/{self.repo_dir}/test/{file_name}")

        self.info("Commit the change of creating a new file")
        self.git_client.commit(commit_msg)

        self.info("Get commit logs")
        last_commit = j.sals.process.execute("git log -1", cwd=f"/tmp/{self.repo_dir}/test")

        self.info("Check if commit has been done")
        self.assertIn(commit_msg, str(last_commit))

    def test06_git_commit_one_file(self):
        """Test case for checking a commit with add_all=False.

        **Test Scenario**
        - Get a git client.
        - Create a tow file in repository path.
        - Check that tow file has been added.
        - Commit the file 1.
        - Check if commit has been done for one file.
        """
        file1_name = self.random_name()
        file2_name = self.random_name()

        self.info("Create a tow file in repository path")
        j.sals.fs.touch(f"/tmp/{self.repo_dir}/test/{file1_name}")
        j.sals.fs.touch(f"/tmp/{self.repo_dir}/test/{file2_name}")

        self.info("Check that tow file has been added.")
        self.assertEqual([file2_name, file1_name].sort(), self.git_client.get_modified_files()["N"].sort())

        self.info("Commit the file 1")
        j.sals.process.execute(f"git add {file1_name}", cwd=f"/tmp/{self.repo_dir}/test")
        self.git_client.commit("commit file 1", add_all=False)

        self.info("Check if commit has been done for one file")
        self.assertNotIn(file1_name, self.git_client.get_modified_files()["N"])

    def test07_git_pull(self):
        """Test case for pull from repository

        **Test Scenario**
        - Get a git client.
        - Create a file in repository path.
        - Try pull befor commit and should get error.
        - Commit the change of creating a new file.
        - Pull from remote repository.
        """
        file_name = self.random_name()
        commit_msg = self.random_name()

        self.info("Create a file in repository path")
        j.sals.fs.touch(f"/tmp/{self.repo_dir}/test/{file_name}")

        self.info("Try pull befor commit and should get error")
        with self.assertRaises(j.exceptions.Input):
            self.git_client.pull()

        self.info("Commit the change of creating a new file")
        self.git_client.commit(commit_msg)

        self.info("Pull from remote repository")
        self.git_client.pull()
