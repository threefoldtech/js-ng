import string

from jumpscale.loader import j
from tests.base_tests import BaseTests


class GitTests(BaseTests):
    def setUp(self):
        super().setUp()
        self.instance_name = self.random_name()
        self.repo_dir = f"/tmp/{self.random_name()}"
        self.repo_name = "js-ng"
        self.repo_url = "https://github.com/threefoldtech/js-ng"
        j.sals.fs.mkdir(f"{self.repo_dir}")
        j.sals.process.execute(f"git clone {self.repo_url}", cwd=f"{self.repo_dir}")
        self.git_client = j.clients.git.new(name=self.instance_name, path=f"{self.repo_dir}/{self.repo_name}/")

    def tearDown(self):
        j.clients.git.delete(self.instance_name)
        j.sals.fs.rmtree(path=f"{self.repo_dir}")

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
        git_config = j.sals.fs.read_file(f"{self.repo_dir}/{self.repo_name}/.git/config")

        self.info("Check that remote_url equal to repo_url")
        self.assertEqual(self.repo_url, self.git_client.remote_url)

        self.info("Check that git config url equal to remote_url")
        self.assertIn(self.git_client.remote_url, git_config)

    def test02_git_branch(self):
        """Test case for checking a branch name.

        **Test Scenario**
        - Get a git client.
        - Get the branch name.
        - Check branch name.
        """
        self.info("Get the branch name")
        branch_name = j.sals.process.execute("git branch", cwd=f"{self.repo_dir}/{self.repo_name}")

        self.info("Check branch name")
        self.assertIn(self.git_client.branch_name, branch_name[1])

    def test03_git_modifed_files(self):
        """Test case for getting the modifed files.

        **Test Scenario**
        - Get a git client.
        - Create a file in repository path.
        - Commit changes
        - modify this file
        - Check if file has been modifed
        """
        self.info("Create a file in repository path")
        file_name = self.random_name()
        j.sals.fs.touch(f"{self.repo_dir}/{self.repo_name}/{file_name}")

        self.info("Commit changes")
        self.git_client.commit(f"add {file_name}")

        self.info("modify this file")
        j.sals.fs.write_file(f"{self.repo_dir}/{self.repo_name}/{file_name}", "test modify file")

        self.info("Check if file has been modifed")
        modided_file = self.git_client.get_modified_files()
        self.assertNotEqual(len(modided_file), 0)
        self.assertEqual(file_name, modided_file["M"][0])

    def test04_git_add_new_file(self):
        """Test case for adding a new file with git.

        **Test Scenario**
        - Get a git client.
        - Create a file in repository path.
        - Check if a new file has been added
        """
        self.info("Create a file in repository path")
        file_name = self.random_name()
        j.sals.fs.touch(f"{self.repo_dir}/{self.repo_name}/{file_name}")

        self.info("Check if a new file has been added")
        added_file = self.git_client.get_modified_files()
        self.assertNotEqual(len(added_file), 0)
        self.assertEqual(file_name, added_file["N"][0])

    def test05_git_commit(self):
        """Test case for committing a change.

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
        j.sals.fs.touch(f"{self.repo_dir}/{self.repo_name}/{file_name}")

        self.info("Commit the change of creating a new file")
        self.git_client.commit(commit_msg)

        self.info("Get commit logs")
        last_commit = j.sals.process.execute("git log -1", cwd=f"{self.repo_dir}/{self.repo_name}")

        self.info("Check if commit has been done")
        self.assertIn(commit_msg, str(last_commit))

    def test06_git_commit_one_file(self):
        """Test case for checking a commit with add_all=False.

        **Test Scenario**
        - Get a git client.
        - Create a two file in repository path.
        - Check that two file has been added.
        - Commit the file 1.
        - Check if commit has been done for one file.
        """
        file1_name = self.random_name()
        file2_name = self.random_name()

        self.info("Create a two file in repository path")
        j.sals.fs.touch(f"{self.repo_dir}/{self.repo_name}/{file1_name}")
        j.sals.fs.touch(f"{self.repo_dir}/{self.repo_name}/{file2_name}")

        self.info("Check that two file has been added.")
        self.assertEqual([file2_name, file1_name].sort(), self.git_client.get_modified_files()["N"].sort())

        self.info("Commit the file 1")
        j.sals.process.execute(f"git add {file1_name}", cwd=f"{self.repo_dir}/{self.repo_name}")
        self.git_client.commit("commit file 1", add_all=False)

        self.info("Check if commit has been done for one file")
        self.assertNotIn(file1_name, self.git_client.get_modified_files()["N"])

    def test07_git_pull(self):
        """Test case for pulling a repository

        **Test Scenario**
        - Get a git client.
        - Create a file in repository path.
        - Try pull before commit and should get error.
        - Commit the change of creating a new file.
        - Pull from remote repository.
        """
        file_name = self.random_name()
        commit_msg = self.random_name()

        self.info("Create a file in repository path")
        j.sals.fs.touch(f"{self.repo_dir}/{self.repo_name}/{file_name}")

        self.info("Try pull before commit and should get error")
        with self.assertRaises(j.exceptions.Input):
            self.git_client.pull()

        self.info("Commit the change of creating a new file")
        self.git_client.commit(commit_msg)

        self.info("Pull from remote repository")
        self.git_client.pull()
