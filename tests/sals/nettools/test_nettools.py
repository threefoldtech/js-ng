import pytest
import jumpscale.sals.nettools as nettools
import time
import subprocess
import concurrent.futures
import socketserver


@pytest.mark.parametrize("ipaddr, port, timeout", [("1.1.1.1", 53, 5), ("8.8.8.8", 53, 5), ("www.google.com", 80, 5)])
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
def test_02_tcp_connection_test_to_public_ip_timeed_out(ipaddr, port, timeout):
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


@pytest.mark.parametrize("server_status_code", [200, 201, 202, 203, 204, 205, 206])
def test_04_wait_http_test_succeed(server_status_code):
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


def test_05_wait_http_test_timed_out():
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
def test_06_check_url_reachable_succeed(server_status_code, verify, fake_user_agent):
    """Test case for sending get request to specified url and check if it is reachable
    (get 2xx http response) or {timeout} elapsed

    **Test Scenario**

    - Execute the function check_url_reachable_succeed and send requests to custom url that mimic different responses
      to test againest specified list of responses (considered reachable 2xx)
    - test while verifying the servers TLS certificate turned on and off
    - test while fakeing user agnet turned on and off
    - check the function result.
    """

    url = f"https://httpbin.org/status/{server_status_code}"
    is_reachable = nettools.check_url_reachable(url, verify=verify, fake_user_agent=fake_user_agent)

    assert is_reachable


@pytest.mark.parametrize("server_status_code", [400, 403, 500, 501, 503])
def test_07_check_url_reachable_failed(server_status_code):
    """Test case for sending get request to specified url and check if it is reachable
    (get 2xx http response) or {timeout} elapsed

    **Test Scenario**

    - Execute the function check_url_reachable_succeed and send requests to custom url that mimic different responses
      to test againest specified list of responses (considered unreachable 4xx, 5xx)
    - check the function result.
    """

    url = f"http://httpbin.org/status/{server_status_code}"
    is_reachable = nettools.check_url_reachable(url)

    assert not is_reachable
