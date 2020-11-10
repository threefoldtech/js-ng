### test01_execute

Test case for executing command.

**Test Scenario**

- Execute command.
- Check the command result.

### test02_execute_with_env

Test case for executing command with environment variable.

**Test Scenario**

- Execute command with environment variable.
- Check that the environment varible is exist.

### test_03_execute_with_timeout

Test case for executing command with timeout.

**Test Scenario**

- Execute command with timeout.
- Make sure that the command will raise timeout error.

### test_04_execute_with_die

Test case for executing command with die.

**Test Scenario**

- Execute command with die.
- Make sure that the command will raise error.

### test_05_execute_with_cwd

Test case for executing command with working directory.

**Test Scenario**

- Create a directory with one file.
- Execute command in the directory has been created.
- Check that the command will run on the directory has been created.
- Delete created file and directory.

### test_06_check_for_pid_process

Test case for checking that the pid and process name are belong to the same process.

**Test Scenario**

- Start a process in tmux.
- Get process id.
- Check that the pid and process name are belong to the same process.

### test_07_check_running

Test case for checking that process is running.

**Test Scenario**

- Start a process in tmux.
- Check that the process is running with one minimum instance, should be True.
- Check that the process is running with two minimum instance, should be False.
- Start another process in tmux.
- Check that the process is running with two minimum instance, should be True.

### test_08_check_start_stop

Test case for checking starting and stopping command.

**Test Scenario**

- Start a process in tmux with check_start.
- Check that the process has been started.
- Stop the process.
- Check that the process has been stopped.
- Start a process again in tmux with nrinstances=2, should fail.

### test_09_get_process_environ

Test case for getting process environment variables.

**Test Scenario**

- Start a tail command with environment variable.
- Check that the process has been started and get its pid.
- Get this process environ with its pid.
- Check that the environment variable has been set is in process environ.

### test_10_get_filtered_pids

Test case for getting filtered process pid.

**Test Scenario**

- Start a tmux session with two python server process.
- Check that the process has been started and get its pid.
- Get this process pid with its name.
- Check that there is two pids.
- Get this process pid with its name and filtered with server port.
- Check that only one server is found.

### test_11_get_memory_usage

Test case for getting memory usage.

**Test Scenario**

- Get memory usage from SALS process.
- Get memory usage from 'free' command.
- Check that memory usage from both ways almost the same.

### test_12_get_processes_info

Test case for getting processes info.

**Test Scenario**

- Start python server in tmux.
- Check that the server has been started.
- Get processes self.info using SALS process.
- Check that the python server is in the processes self.info.
- Get the current process using SALS process.
- Check that this process in processes self.info.

### test_13_get_kill_process_by_port

Test case for getting and killing process by its port.

**Test Scenario**

- Start python server in tmux.
- Check that the server has been started.
- Get the process by port.
- Get pid of the process by port.
- Check that the python server pid is the same one from SALS process.
- Kill the server by port.
- Check that the server pid is not exist.

### test_14_is_installed

Test case for is_installed method.

**Test Scenario**

- Check that a package should be installed with js-ng.
- Check that any random name is not installed.

### test_15_get_kill_process_by_pids

Test case for getting and killing process by pids.

**Test Scenario**

- Start a tail process in tmux.
- Check that the process has been started.
- Get the process pids.
- Check that the process pid is alive.
- Kill the process.
- Check that the process has been killed.

### test_16_get_kill_user_process_0_kill_all

Test case for getting and killing user process/ killall processes [with kill_method='kill_all'].

**Test Scenario**

- Start a tail process in tmux with the current user.
- Check that the process has been started.
- Create a user.
- Start another tail process in tmux with new user.
- Check that the process has been started.
- Get the user process.
- Check that the process is the new user process.
- Kill the user/killall process, and check that the target process killed.

### test_16_get_kill_user_process_1_kill_user_processes

Test case for getting and killing user process/ killall processes [with kill_method='kill_user_processes'].

**Test Scenario**

- Start a tail process in tmux with the current user.
- Check that the process has been started.
- Create a user.
- Start another tail process in tmux with new user.
- Check that the process has been started.
- Get the user process.
- Check that the process is the new user process.
- Kill the user/killall process, and check that the target process killed.

### test_16_get_kill_user_process_2_kill_process_by_name

Test case for getting and killing user process/ killall processes [with kill_method='kill_process_by_name'].

**Test Scenario**

- Start a tail process in tmux with the current user.
- Check that the process has been started.
- Create a user.
- Start another tail process in tmux with new user.
- Check that the process has been started.
- Get the user process.
- Check that the process is the new user process.
- Kill the user/killall process, and check that the target process killed.

### test_17_check_in_docker

Test case for Checking if in docker or in host.

**Test Scenario**

- Check if in docker/host with dockerenv file.
- Check if in docker/host with Sals.
- Check that the result from both ways are the same.

### test_18_ps_find

Test case for Checking if process exists.

**Test Scenario**

- Start a tail process.
- Check that the process has been started.
- Check that the process exists, should be found.
- Check for a random name, should not be found.

### test_19_set_env_var

Test case for setting environment variable.

**Test Scenario**

- Set environment variable with SAL.
- Check that the environment variable is set.
- Set environment variable with non equal length, should fail.

### test_20_get_ports_mapping

Test case for getting port mapping.

**Test Scenario**

- Start python server.
- Check that the server has been started.
- Start redis server.
- Check that the server has been started.
- Get port mapping with netstat command.
- Get port mapping with SAL.
- Check that the result from both ways are the same.

### test_21_get_defunct_processes

Test case for getting defunct processes.

**Test Scenario**

- Start a dummy zombie process.
- Get zombie processes with ps command.
- Get zombie processes with sal.
- Check that the both ways have the same result.

### test_22_get_sorted_pids_0_sorted

Test case for getting sorted pids by username [with type_='sorted'].

**Test Scenario**

- Start a tail process from the currnet user.
- Create two users and start tail process for each user.
- Get each user pids.
- Get pids sorted with username.
- Check that the pids are sorted.
- Get tail pids with regex filter.
- Check that only pids that match the regex are returned.

### test_22_get_sorted_pids_1_regex

Test case for getting sorted pids by username [with type_='regex'].

**Test Scenario**

- Start a tail process from the currnet user.
- Create two users and start tail process for each user.
- Get each user pids.
- Get pids sorted with username.
- Check that the pids are sorted.
- Get tail pids with regex filter.
- Check that only pids that match the regex are returned.
