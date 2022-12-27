### test_01_tcp_connection_test_to_public_ipv4_succeed[1.1.1.1-53-5]

Test case to establish a connection to specified address and initiate
the three-way handshake and check if the connection succeeded.

**Test Scenario**

- Connect to publicly available services that have a known ip and a tcp
port open. test using ip or hostname
- Check the connection result. should return True.

### test_01_tcp_connection_test_to_public_ipv4_succeed[8.8.8.8-53-5]

Test case to establish a connection to specified address and initiate
the three-way handshake and check if the connection succeeded.

**Test Scenario**

- Connect to publicly available services that have a known ip and a tcp
port open. test using ip or hostname
- Check the connection result. should return True.

### test_01_tcp_connection_test_to_public_ipv4_succeed[www.google.com-80-5]

Test case to establish a connection to specified address and initiate
the three-way handshake and check if the connection succeeded.

**Test Scenario**

- Connect to publicly available services that have a known ip and a tcp
port open. test using ip or hostname
- Check the connection result. should return True.

### test_02_tcp_connection_test_to_public_ipv4_timed_out[1.1.1.1-52-2]

Test case for establish a connection to specified address and initiate
the three-way handshake where the port is unreachable and check if the
connection will timeout.

**Test Scenario**

- Try to connect to publicly available services but using wrong tcp ports.
- Check the connection result. should timeout after 2 sec and return False.

### test_02_tcp_connection_test_to_public_ipv4_timed_out[8.8.8.8-52-2]

Test case for establish a connection to specified address and initiate
the three-way handshake where the port is unreachable and check if the
connection will timeout.

**Test Scenario**

- Try to connect to publicly available services but using wrong tcp ports.
- Check the connection result. should timeout after 2 sec and return False.

### test_02_tcp_connection_test_to_public_ipv4_timed_out[www.google.com-70-2]

Test case for establish a connection to specified address and initiate
the three-way handshake where the port is unreachable and check if the
connection will timeout.

**Test Scenario**

- Try to connect to publicly available services but using wrong tcp ports.
- Check the connection result. should timeout after 2 sec and return False.

### test_03_wait_connection_test_ipv4_succeed

Test case for waiting until port listens on the specified address

**Test Scenario**

- Execute the function wait_connection_test on a new thread to wait for a tcp on random free port on the local host.
- Wait 4 sec.
- Run netcat command to start listen on that port.
- Check the function result.

### test_04_wait_connection_test_ipv6_succeed

Test case for waiting until port listens on the specified address

**Test Scenario**

- Execute the function wait_connection_test on a new thread to wait for a tcp on random free port on the local host.
- Wait 4 sec.
- Run netcat command to start listen on that port.
- Check the function result.

### test_05_wait_http_test_succeed[200]

Test case for trying to reach specified url every default interval time sec
until url become reachable (get 2xx http response) or {timeout} elapsed

**Test Scenario**

- Execute the function wait_http_test on a new thread to send get request to localhost on a random free port
every default interval seconds and wait for 2xx response back.
- Wait 2 sec.
- Start http server on localhost
- Check the function result.

### test_05_wait_http_test_succeed[201]

Test case for trying to reach specified url every default interval time sec
until url become reachable (get 2xx http response) or {timeout} elapsed

**Test Scenario**

- Execute the function wait_http_test on a new thread to send get request to localhost on a random free port
every default interval seconds and wait for 2xx response back.
- Wait 2 sec.
- Start http server on localhost
- Check the function result.

### test_05_wait_http_test_succeed[202]

Test case for trying to reach specified url every default interval time sec
until url become reachable (get 2xx http response) or {timeout} elapsed

**Test Scenario**

- Execute the function wait_http_test on a new thread to send get request to localhost on a random free port
every default interval seconds and wait for 2xx response back.
- Wait 2 sec.
- Start http server on localhost
- Check the function result.

### test_05_wait_http_test_succeed[203]

Test case for trying to reach specified url every default interval time sec
until url become reachable (get 2xx http response) or {timeout} elapsed

**Test Scenario**

- Execute the function wait_http_test on a new thread to send get request to localhost on a random free port
every default interval seconds and wait for 2xx response back.
- Wait 2 sec.
- Start http server on localhost
- Check the function result.

### test_05_wait_http_test_succeed[204]

Test case for trying to reach specified url every default interval time sec
until url become reachable (get 2xx http response) or {timeout} elapsed

**Test Scenario**

- Execute the function wait_http_test on a new thread to send get request to localhost on a random free port
every default interval seconds and wait for 2xx response back.
- Wait 2 sec.
- Start http server on localhost
- Check the function result.

### test_05_wait_http_test_succeed[205]

Test case for trying to reach specified url every default interval time sec
until url become reachable (get 2xx http response) or {timeout} elapsed

**Test Scenario**

- Execute the function wait_http_test on a new thread to send get request to localhost on a random free port
every default interval seconds and wait for 2xx response back.
- Wait 2 sec.
- Start http server on localhost
- Check the function result.

### test_05_wait_http_test_succeed[206]

Test case for trying to reach specified url every default interval time sec
until url become reachable (get 2xx http response) or {timeout} elapsed

**Test Scenario**

- Execute the function wait_http_test on a new thread to send get request to localhost on a random free port
every default interval seconds and wait for 2xx response back.
- Wait 2 sec.
- Start http server on localhost
- Check the function result.

### test_06_wait_http_test_timed_out

Test case for trying to reach specified url every default interval time sec
 but timed out before getting 2xx http response

**Test Scenario**

- Execute the function wait_http_test with 1 sec timeout on a new thread
- Wait 2 sec.
- Check running thread if the function timed out or still running.

### test_07_check_url_reachable_succeed[200-True-True]

Test case for sending get request to specified url and check if it is reachable
(get 2xx http response) or {timeout} elapsed

**Test Scenario**

- Execute the function check_url_reachable and send requests to custom url that mimic different responses
to test against a specified list of responses (considered reachable 2xx)
- Test while verifying the servers TLS certificate turned on and off
- Test while faking user agent turned on and off
- Check the function result.

### test_07_check_url_reachable_succeed[201-True-True]

Test case for sending get request to specified url and check if it is reachable
(get 2xx http response) or {timeout} elapsed

**Test Scenario**

- Execute the function check_url_reachable and send requests to custom url that mimic different responses
to test against a specified list of responses (considered reachable 2xx)
- Test while verifying the servers TLS certificate turned on and off
- Test while faking user agent turned on and off
- Check the function result.

### test_07_check_url_reachable_succeed[202-True-True]

Test case for sending get request to specified url and check if it is reachable
(get 2xx http response) or {timeout} elapsed

**Test Scenario**

- Execute the function check_url_reachable and send requests to custom url that mimic different responses
to test against a specified list of responses (considered reachable 2xx)
- Test while verifying the servers TLS certificate turned on and off
- Test while faking user agent turned on and off
- Check the function result.

### test_07_check_url_reachable_succeed[203-False-False]

Test case for sending get request to specified url and check if it is reachable
(get 2xx http response) or {timeout} elapsed

**Test Scenario**

- Execute the function check_url_reachable and send requests to custom url that mimic different responses
to test against a specified list of responses (considered reachable 2xx)
- Test while verifying the servers TLS certificate turned on and off
- Test while faking user agent turned on and off
- Check the function result.

### test_07_check_url_reachable_succeed[204-False-False]

Test case for sending get request to specified url and check if it is reachable
(get 2xx http response) or {timeout} elapsed

**Test Scenario**

- Execute the function check_url_reachable and send requests to custom url that mimic different responses
to test against a specified list of responses (considered reachable 2xx)
- Test while verifying the servers TLS certificate turned on and off
- Test while faking user agent turned on and off
- Check the function result.

### test_07_check_url_reachable_succeed[205-False-True]

Test case for sending get request to specified url and check if it is reachable
(get 2xx http response) or {timeout} elapsed

**Test Scenario**

- Execute the function check_url_reachable and send requests to custom url that mimic different responses
to test against a specified list of responses (considered reachable 2xx)
- Test while verifying the servers TLS certificate turned on and off
- Test while faking user agent turned on and off
- Check the function result.

### test_07_check_url_reachable_succeed[206-True-False]

Test case for sending get request to specified url and check if it is reachable
(get 2xx http response) or {timeout} elapsed

**Test Scenario**

- Execute the function check_url_reachable and send requests to custom url that mimic different responses
to test against a specified list of responses (considered reachable 2xx)
- Test while verifying the servers TLS certificate turned on and off
- Test while faking user agent turned on and off
- Check the function result.

### test_08_check_url_reachable_failed[400]

Test case for sending get request to specified url and check if it is reachable
(get 2xx http response) or {timeout} elapsed

**Test Scenario**

- Execute the function check_url_reachable and send requests to custom url that mimic different responses
to test against a specified list of responses (considered unreachable 4xx, 5xx)
- Check the function result.

### test_08_check_url_reachable_failed[403]

Test case for sending get request to specified url and check if it is reachable
(get 2xx http response) or {timeout} elapsed

**Test Scenario**

- Execute the function check_url_reachable and send requests to custom url that mimic different responses
to test against a specified list of responses (considered unreachable 4xx, 5xx)
- Check the function result.

### test_08_check_url_reachable_failed[500]

Test case for sending get request to specified url and check if it is reachable
(get 2xx http response) or {timeout} elapsed

**Test Scenario**

- Execute the function check_url_reachable and send requests to custom url that mimic different responses
to test against a specified list of responses (considered unreachable 4xx, 5xx)
- Check the function result.

### test_08_check_url_reachable_failed[501]

Test case for sending get request to specified url and check if it is reachable
(get 2xx http response) or {timeout} elapsed

**Test Scenario**

- Execute the function check_url_reachable and send requests to custom url that mimic different responses
to test against a specified list of responses (considered unreachable 4xx, 5xx)
- Check the function result.

### test_08_check_url_reachable_failed[503]

Test case for sending get request to specified url and check if it is reachable
(get 2xx http response) or {timeout} elapsed

**Test Scenario**

- Execute the function check_url_reachable and send requests to custom url that mimic different responses
to test against a specified list of responses (considered unreachable 4xx, 5xx)
- Check the function result.

### test_09_udp_connection_test[8.8.8.8-53-5-\xaa\xaa\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07example\x03com\x00\x00\x01\x00\x01]

Test case for create udp socket and sending specified message the specified ip and udp port
and wait to receive at least one byte from the socket

**Test Scenario**

- Execute the function udp_connection_test, connect to dns.google.com on udp port 53
with manually craft dns query message and wait for at least one byte.
- Check the function result.

### test_10_get_nic_names

Test case for getting a list of all available nics

**Test Scenario**

- Execute the function get_nic_names
- Check the function result if we got non empty list

### test_11_get_reachable_ip_address_local[127.0.0.1]

Test case for getting the source address that would be used if some traffic were to be sent out to specified ip

**Test Scenario**

- Execute the function get_reachable_ip_address uses both ipv4, ipv6 localhost address
- Check the function result. expected same ip address used (only because tested with localhost ip address)

### test_11_get_reachable_ip_address_local[::1]

Test case for getting the source address that would be used if some traffic were to be sent out to specified ip

**Test Scenario**

- Execute the function get_reachable_ip_address uses both ipv4, ipv6 localhost address
- Check the function result. expected same ip address used (only because tested with localhost ip address)

### test_12_get_default_ip_config[127.0.0.10-expected0]

Test case for getting default nic name and its ip address
that would be used if some traffic were to be sent out to specified ip

**Test Scenario**

- Execute the function get_reachable_ip_address uses both ipv4, ipv6 localhost address
- Check the function result. expected same ip address used (only because tested with localhost ip address)

### test_12_get_default_ip_config[::1-expected1]

Test case for getting default nic name and its ip address
that would be used if some traffic were to be sent out to specified ip

**Test Scenario**

- Execute the function get_reachable_ip_address uses both ipv4, ipv6 localhost address
- Check the function result. expected same ip address used (only because tested with localhost ip address)

### test_13_get_network_info

Test case for getting the expected structure from calling get_network_info

**Test Scenario**

- Execute the function get_network_info without args
- Check the function result. expected to get a list of dicts

### test_14_get_network_info_specific_device_loopback

Test case for getting the expected structure from calling get_network_info

**Test Scenario**

- Execute the function get_network_info with loopback device as arg
- Check the function result. expected to get a dict

### test_15_get_mac_address

Test case for getting the MAC address all network interfaces in the machine

**Test Scenario**

- Execute the function get_nic_names to get list of all nics
- Loop through the list and call get_mac_address function
- Check the function result for every interface name. expected to get 6 groups of characters separated by colon

### test_16_is_nic_connected

Test case for check whether interface is up or down

**Test Scenario**

- Execute the function get_nic_names to get list of all nics
- Loop through the list and call is_nic_connected function
- Check the function result for every interface name. expected to get a bool type

### test_17_is_nic_connected[lo-True]

Test case for check whether interface is up or down

**Test Scenario**

- Execute the function get_nic_names with lo interface as arg and expect it to be up
- Check the function result. should return True

### test_18_ping_machine_success[127.0.0.1-4-False]

Test case for check whether machine is up/running and accessible

**Test Scenario**

- Execute the function ping_machine once with localhost ipv4 and ipv6 addresses and with a local machine hostname
- Check the function result. should return True

### test_18_ping_machine_success[localhost-4-True]

Test case for check whether machine is up/running and accessible

**Test Scenario**

- Execute the function ping_machine once with localhost ipv4 and ipv6 addresses and with a local machine hostname
- Check the function result. should return True

### test_18_ping_machine_success[::1-4-False]

Test case for check whether machine is up/running and accessible

**Test Scenario**

- Execute the function ping_machine once with localhost ipv4 and ipv6 addresses and with a local machine hostname
- Check the function result. should return True

### test_19_ping_machine_timeout[10.200.199.198-1-False]

Test case for check whether the ping_machine will timeout after specified number of seconds

**Test Scenario**

- Execute the function ping_machine with probably unused private ip address and 1 seconds timeout on a new thread
- Wait for 2 seconds
- Check running thread if the function timed out or still running and if it returned False

### test_20_ping_machine_exception[www.google.com-2-False]

Test case for check whether the ping_machine will raise exception when it receive a host name while allowhostname is false

**Test Scenario**

- Execute the function ping_machine with a hostname
- Assert the raised exception

### test_21_download_ftp[ftp://ftp.sas.com/techsup/download/TestSSLServer4.zip-test_21_downloaded-None-None-True-False-False]

Test case for download a resource from ftp server

**Test Scenario**

- Execute the function download passing in a ftp link and a localpath consists of just filename
- Assert the downloaded file successfully downloaded.
- Assert the downloaded file have the correct name
- Assert the downloaded file exists in the current working directory
- Remove the file

### test_22_download_https[https://pypi.org/project/js-ng/-test_22_downloaded-None-None-True-False-False]

Test case for download a resource from https link

**Test Scenario**

- Execute the function download passing in a https link and a localpath consists of just filename
- Assert the downloaded file successfully downloaded.
- Assert the downloaded file have the correct name
- Assert the downloaded file exists in the current working directory
- Remove the file

### test_23_download_http[http://ftp.sas.com/techsup/download/TestSSLServer4.txt-test_23_downloaded-None-None-True-False-False]

Test case for download a resource from http link

**Test Scenario**

- Execute the function download passing in a http link and a localpath consists of just filename
- Assert the downloaded file successfully downloaded.
- Assert the downloaded file have the correct name
- Assert the downloaded file exists in the current working directory
- Remove the file

### test_24_download_append_to_home[ftp://ftp.sas.com/techsup/download/TestSSLServer4.zip-test_24_downloaded-None-None-True-True-False]

Test case for download a resource from url to localpath relative to user home directory

**Test Scenario**

- Execute the function download passing in an url and a localpath consists of just filename.
- Assert the downloaded file successfully downloaded.
- Assert the downloaded file have the correct name
- Assert the downloaded file exists in the user home directory
- Remove the file

### test_25_download_create_parents[https://pypi.org/project/js-ng/-downloaded_test_25/files/test_25_downloaded-None-None-True-False-False]

Test case for download a resource from url to localpath that don't exists

**Test Scenario**

- Execute the function download passing in an url and a localpath consists chain of directories that not exists
- Assert the downloaded file successfully downloaded.
- Assert the downloaded file have the correct name
- Assert the parents' directories successfully created
- Remove the file, and its parents' dir

### test_26_download_name_from_url[http://ftp.sas.com/techsup/download/TestSSLServer4.txt--None-None-True-False-True]

Test case for download a resource from url to cwd and get the filename from the url

**Test Scenario**

- Execute the function download passing in an url and a localpath consists of an empty string
- Assert the downloaded file successfully downloaded.
- Assert tha downloaded file have correct name from the url
- Remove the file

### test_27_download_overwrite_False[http://ftp.sas.com/techsup/download/TestSSLServer4.txt-downloaded_test_27-None-None-False-False-False]

Test case for download a resource from url to localpath when the file already exists

**Test Scenario**

- Execute the function download passing in an url and a localpath consists of the desired filename and assigning False to overwrite
- Assert the raised exception

### test_28_download_overwrite_True[http://ftp.sas.com/techsup/download/TestSSLServer4.txt-downloaded_test_28-None-None-True-False-False]

Test case for download a resource from url to localpath when the file already exists

**Test Scenario**

- Execute the function download passing in an url and a localpath consists of the desired filename and assigning True to overwrite
- Assert the result
- Execute the function download again passing in the same url and the same localpath and assigning True to overwrite
- Remove the file

### test_29_download_to_unwritable_dir[http://ftp.sas.com/techsup/download/TestSSLServer4.txt-unwriteable_dir-None-None-False-True-True]

Test case for download a resource from url to localpath when user don't have proper Permissions

**Test Scenario**

- Execute the function download passing in an url and a localpath
- Create the dir
- Set the dir permissions to make it unwritable
- Assert the raised exception when try to download a file to this dir
- Reset the dir permissions and delete it

### test_30_download_return_content[http://ftp.sas.com/techsup/download/TestSSLServer4.txt-None-None-None-False-False-True]

Test case for download a resource from url and return the content

**Test Scenario**

- Execute the function download passing in an url and set localpath to None
- Assert that we got the content
- Assert that returned content size is equal to one from the response headers

### test_31_get_free_port

Test case for getting free ports and use it.

**Test Scenario**

- Execute the function get_free_port many time (500)
- The function will bind the port to 127.0.0.1 and return a socket
- As long as no OSError exception (in case if port already in use) the port selected by the function (by OS) is free
- Clean up and close all sockets
