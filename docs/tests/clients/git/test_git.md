### test01_check_git_config

Test case for checking git config file.

**Test Scenario**
- Get a git client.
- Read the git.config file.
- Check that remote_url equal to repo_url.
- Check that url equal to remote_url.

### test02_set_remote_ssh_url

Test case for setting remote url.

**Test Scenario**
- Get a git client.
- Set remote url to repo ssh url.
- Read the git config file.
- Check that remote_url equals to repo ssh url.

### test03_git_branch

Test case for checking a branch name.

**Test Scenario**
- Get a git client.
- Get the branch name.
- Check branch name.

### test04_git_modified_files

Test case for getting the modified files.

**Test Scenario**
- Get a git client.
- Create a file in repository path.
- Commit changes
- modify this file
- Check if file has been modified

### test05_git_add_new_file

Test case for adding a new file with git.

**Test Scenario**
- Get a git client.
- Create a file in repository path.
- Check if a new file has been added

### test06_git_commit

Test case for committing a change.

**Test Scenario**
- Get a git client.
- Create a file in repository path.
- Commit the change of creating a new file.
- Get commit logs.
- Check if commit has been done.

### test07_git_commit_one_file

Test case for checking a commit with add_all=False.

**Test Scenario**
- Get a git client.
- Create a two file in repository path.
- Check that two file has been added.
- Commit the file 1.
- Check if commit has been done for one file.

### test08_git_pull

Test case for pulling a repository

**Test Scenario**
- Get a git client.
- Create a file in repository path.
- Try pull before commit and should get error.
- Commit the change of creating a new file.
- Pull from remote repository.
