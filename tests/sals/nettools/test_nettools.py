import pytest
import jumpscale.sals.nettools as nettools
import time
import subprocess
import concurrent.futures
import socketserver
import socket
import ipaddress
from jumpscale.core.exceptions import Value, Runtime


@pytest.mark.parametrize("ipaddr, port, timeout", [("1.1.1.1", 53, 5), ("8.8.8.8", 53, 5), ("www.google.com", 80, 5)])
def test_01_tcp_connection_test_to_public_ipv4_succeed(ipaddr, port, timeout):
    """Test case to establish a connection to specified address and initiate
    the three-way handshake and check if the connection succeded.

    **Test Scenario**

    - connect to Publicly available services that have a known ip and a tcp
      port open. test using ip or hostname
    - Check the connection result. should return True.
    """
    assert nettools.tcp_connection_test(ipaddr, port, timeout)


@pytest.mark.parametrize("ipaddr, port, timeout", [("1.1.1.1", 52, 2), ("8.8.8.8", 52, 2), ("www.google.com", 70, 2)])
def test_02_tcp_connection_test_to_public_ipv4_timed_out(ipaddr, port, timeout):
    """Test case for establish a connection to specified address and initiate
    the three-way handshake where the port is unreachable and check if the
    connection will timeout.

    **Test Scenario**

    - try to connect to Publicly available services put using worng tcp ports.
    - Check the connection result. should timeout after 2 sec and return False.
    """
    assert not nettools.tcp_connection_test(ipaddr, port, timeout)


def test_03_wait_connection_test_ipv4_succeed():
    """Test case for waiting until port listens on the specified address

    **Test Scenario**

    - Execute the function wait_connection_test on a new thread to wait for a tcp on random free port on the local host.
    - wait 4 sec.
    - run netcat command to start listen on that port.
    - check the function result.
    """
    TIMEOUT = 6
    # getting random free port
    with socketserver.TCPServer(("localhost", 0), None) as s:
        port = s.server_address[1]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(nettools.wait_connection_test, "::1", port, TIMEOUT)
        time.sleep(4)
        subprocess.Popen(["nc", "-l", "::1", str(port)])
        return_value = future.result()

    assert return_value


def test_04_wait_connection_test_ipv6_succeed():
    """Test case for waiting until port listens on the specified address

    **Test Scenario**

    - Execute the function wait_connection_test on a new thread to wait for a tcp on random free port on the local host.
    - wait 4 sec.
    - run netcat command to start listen on that port.
    - check the function result.
    """
    TIMEOUT = 4
    # getting random free port for ::1
    with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
        s.bind(("::1", 0))
        port = s.getsockname()[1]

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(nettools.wait_connection_test, "::1", port, TIMEOUT)
            time.sleep(1)
            s.listen()
            time.sleep(1)
            return_value = not future.running() and future.result()

    assert return_value


@pytest.mark.parametrize("server_status_code", [200, 201, 202, 203, 204, 205, 206])
def test_05_wait_http_test_succeed(server_status_code):
    """Test case for trying to reach specified url every default interval time sec
    until url become reachable (get 2xx http response) or {timeout} elapsed

    **Test Scenario**

    - Execute the function wait_http_test on a new thread to send get request to localhost on a random free port
      every default interval seconds and wait for 2xx response back.
    - wait 2 sec.
    - start http server on localhost
    - check the function result.
    """
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class MyServer(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(server_status_code)
            self.end_headers()

    def start_http_server(host_name, server_port):

        webServer = HTTPServer((host_name, server_port), MyServer)
        webServer.handle_request()
        webServer.server_close()

    host_name = "localhost"
    # getting random free port
    with socketserver.TCPServer((host_name, 0), None) as s:
        server_port = s.server_address[1]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(nettools.wait_http_test, f"http://{host_name}:{server_port}", 5)
        time.sleep(2)
        _ = executor.submit(start_http_server, host_name, server_port)
        return_value = future.result()
    assert return_value


def test_06_wait_http_test_timed_out():
    """Test case for trying to reach specified url every default interval time sec
     but timed out before getting 2xx http response

    **Test Scenario**

    - Execute the function wait_http_test with 1 sec timeout on a new thread
    - wait 2 sec.
    - check running thread if the function timed out or still running.
    """
    host_name = "localhost"
    # getting random free port
    with socketserver.TCPServer((host_name, 0), None) as s:
        server_port = s.server_address[1]
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(nettools.wait_http_test, f"http://{host_name}:{server_port}", 1)
        time.sleep(2)
        has_timed_out = not future.running()
    assert has_timed_out


@pytest.mark.parametrize(
    "server_status_code, verify, fake_user_agent",
    [
        (200, True, True),
        (201, True, True),
        (202, True, True),
        (203, False, False),
        (204, False, False),
        (205, False, True),
        (206, True, False),
    ],
)
def test_07_check_url_reachable_succeed(server_status_code, verify, fake_user_agent):
    """Test case for sending get request to specified url and check if it is reachable
    (get 2xx http response) or {timeout} elapsed

    **Test Scenario**

    - Execute the function check_url_reachable and send requests to custom url that mimic different responses
      to test againest specified list of responses (considered reachable 2xx)
    - test while verifying the servers TLS certificate turned on and off
    - test while fakeing user agnet turned on and off
    - check the function result.
    """

    url = f"https://httpbin.org/status/{server_status_code}"
    is_reachable = nettools.check_url_reachable(url, verify=verify, fake_user_agent=fake_user_agent)

    assert is_reachable


@pytest.mark.parametrize("server_status_code", [400, 403, 500, 501, 503])
def test_08_check_url_reachable_failed(server_status_code):
    """Test case for sending get request to specified url and check if it is reachable
    (get 2xx http response) or {timeout} elapsed

    **Test Scenario**

    - Execute the function check_url_reachable and send requests to custom url that mimic different responses
      to test againest specified list of responses (considered unreachable 4xx, 5xx)
    - check the function result.
    """

    url = f"http://httpbin.org/status/{server_status_code}"
    is_reachable = nettools.check_url_reachable(url)

    assert not is_reachable


@pytest.mark.parametrize(
    "ipaddr, port, timeout, message",
    [("8.8.8.8", 53, 5, b"\xaa\xaa\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07example\x03com\x00\x00\x01\x00\x01")],
)
def test_09_udp_connection_test(ipaddr, port, timeout, message):
    """Test case for create udp socket and sending specified message the specified ip and udp port
    and wait to receive at least one byte from the socket

    **Test Scenario**

    - Execute the function udp_connection_test, connect to dns.google.com on udp port 53
    with manully craft dns query message and wait for at least one byte.
    - check the function result.
    """
    return_value = nettools.udp_connection_test(ipaddr, port, timeout, message)
    assert return_value


def test_10_get_nic_names():
    """Test case for getting a list of all availabe nics

    **Test Scenario**

    - Execute the function get_nic_names
    - check the function result if we got non empty list
    """
    results = nettools.get_nic_names()
    assert isinstance(results, list) and len(results)


@pytest.mark.parametrize("ip", ["127.0.0.1", "::1"])
def test_11_get_reachable_ip_address_local(ip):
    """Test case for getting the source address that would be used if some traffic were to be sent out to specified ip

    **Test Scenario**

    - Execute the function get_reachable_ip_address uses both ipv4, ipv6 localhost address
    - check the function result. expected same ip address used (only because tested with localhost ip address)
    """
    result = nettools.get_reachable_ip_address(ip)
    assert result == ip


@pytest.mark.parametrize("ip, expected", [("127.0.0.10", ("lo", "127.0.0.1")), ("::1", ("lo", "::1"))])
def test_12_get_default_ip_config(ip, expected):
    """Test case for getting default nic name and its ip address
    that would be used if some traffic were to be sent out to specified ip

    **Test Scenario**

    - Execute the function get_reachable_ip_address uses both ipv4, ipv6 localhost address
    - check the function result. expected same ip address used (only because tested with localhost ip address)
    """
    result = nettools.get_default_ip_config(ip)
    assert result == expected


def test_13_get_network_info():
    """Test case for getting the expected structure from calling get_network_info

    **Test Scenario**

    - Execute the function get_network_info without args
    - check the function result. expected to get a list of dicts
    """
    results = nettools.get_network_info()
    assert isinstance(results, list) and len(results)
    for result in results:
        assert isinstance(result, dict) and all(map(lambda k: k in result.keys(), ["ip", "ip6", "mac", "name"]))


def test_14_get_network_info_specific_device_loopback():
    """Test case for getting the expected structure from calling get_network_info

    **Test Scenario**

    - Execute the function get_network_info with loopback device as arg
    - check the function result. expected to get a dict
    """
    device = "lo"
    result = nettools.get_network_info(device)
    print(result)
    assert isinstance(result, dict) and all(map(lambda k: k in result.keys(), ["ip", "ip6", "mac", "name"]))


def test_15_get_mac_address():
    """Test case for getting the MAC address all network interfaces in the machine

    **Test Scenario**

    - Execute the function get_nic_names to get list of all nics
    - loop through the list and call get_mac_address function
    - check the function result for every interface name. expected to get 6 groups of characters separated by colon
    """
    nic_names = nettools.get_nic_names()
    for nic_name in nic_names:
        mac_addr = nettools.get_mac_address(nic_name)
        assert len(mac_addr.split(":")) == 6


def test_16_is_nic_connected():
    """Test case for check whether interface is up or down

    **Test Scenario**

    - Execute the function get_nic_names to get list of all nics
    - loop through the list and call is_nic_connected function
    - check the function result for every interface name. expected to get a bool type
    """
    nic_names = nettools.get_nic_names()
    for nic_name in nic_names:
        nic_status = nettools.is_nic_connected(nic_name)
        assert isinstance(nic_status, bool)


@pytest.mark.parametrize("interface, expected", [("lo", True)])
def test_17_is_nic_connected(interface, expected):
    """Test case for check whether interface is up or down

    **Test Scenario**

    - Execute the function get_nic_names with lo interface as arg and expect it to be up
    - check the function result. should return True
    """
    nic_status = nettools.is_nic_connected(interface)
    assert nic_status == expected


@pytest.mark.parametrize("ip, timeout, allowhostname", [("1.1.1.1", 4, False), ("www.google.com", 4, True),])
def test_18_ping_machine_success(ip, timeout, allowhostname):
    """Test case for check whether machine is up/running and accessible

    **Test Scenario**

    - Execute the function ping_machine once with puplic ip and once with a puplic hostname
    - check the function result. should return True
    """
    result = nettools.ping_machine(ip, timeout, allowhostname)
    assert result


@pytest.mark.parametrize("ip, timeout, allowhostname", [("10.200.199.198", 1, False),])
def test_19_ping_machine_timeout(ip, timeout, allowhostname):
    """Test case for check whether the ping_machine will timeout after specfied number of seconds

    **Test Scenario**

    - Execute the function ping_machine with probably unused private ip address and 1 seconds timeout on a new thread
    - wait for 2 seconds
    - check running thread if the function timed out or still running and if it returned False
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(nettools.ping_machine, ip, timeout, allowhostname)
        time.sleep(2)
        has_timed_out = not future.running()
        is_false = not future.result()
    assert has_timed_out and is_false


@pytest.mark.parametrize("ip, timeout, allowhostname", [("www.google.com", 2, False),])
def test_19_ping_machine_exception(ip, timeout, allowhostname):

    with pytest.raises(Value):
        nettools.ping_machine(ip, timeout, allowhostname)
