import pytest
import jumpscale.sals.nettools as nettools
import time
import subprocess
import concurrent.futures
import socketserver


@pytest.mark.parametrize("ipaddr, port, timeout", [("1.1.1.1", 53, 5), ("8.8.8.8", 53, 5), ("172.217.21.4", 80, 5)])
def test_01_tcp_connection_test_to_public_ip_succeed(ipaddr, port, timeout):
    """Test case to establish a connection to specified address and initiate
    the three-way handshake and check if the connection succeded.

    **Test Scenario**

    - connect to Publicly available services that have a known ip and a tcp
      port open.
    - Check the connection result. should return True.
    """
    assert nettools.tcp_connection_test(ipaddr, port, timeout)


@pytest.mark.parametrize("ipaddr, port, timeout", [("1.1.1.1", 52, 2), ("8.8.8.8", 52, 2), ("172.217.21.4", 70, 2)])
def test_02_tcp_connection_test_to_public_ip_timeout(ipaddr, port, timeout):
    """Test case for establish a connection to specified address and initiate
    the three-way handshake where the port is unreachable and check if the
    connection will timeout.

    **Test Scenario**

    - try to connect to Publicly available services put using worng tcp ports.
    - Check the connection result. should timeout after 2 sec and return False.
    """
    assert not nettools.tcp_connection_test(ipaddr, port, timeout)


def test_03_wait_connection_test_succeed():
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
        future = executor.submit(nettools.wait_connection_test, "127.0.0.1", port, TIMEOUT)
        time.sleep(4)
        subprocess.Popen(["nc", "-l", str(port)])
        return_value = future.result()

    assert return_value
