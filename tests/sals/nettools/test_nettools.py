import pytest
import jumpscale.sals.nettools as nettools


@pytest.mark.parametrize("ipaddr, port, timeout", [("1.1.1.1", 53, 5), ("8.8.8.8", 53, 5), ("172.217.21.4", 80, 5)])
def test_01_tcp_connection_test_to_plublic_ip_succeed(ipaddr, port, timeout):
    """Test case to establish a connection to specified address and initiate
    the three-way handshake and check if the connection succeded.

    **Test Scenario**

    - connect to Publicly available services that have a known ip and a tcp
      port open.
    - Check the connection result. should return True.
    """
    assert nettools.tcp_connection_test(ipaddr, port, timeout)


@pytest.mark.parametrize("ipaddr, port, timeout", [("1.1.1.1", 52, 2), ("8.8.8.8", 52, 2), ("172.217.21.4", 70, 2)])
def test_02_tcp_connection_test_to_plublic_ip_timeout(ipaddr, port, timeout):
    """Test case for establish a connection to specified address and initiate
    the three-way handshake where the port is unreachable and check if the
    connection will timeout.

    **Test Scenario**

    - try to connect to Publicly available services put using worng tcp ports.
    - Check the connection result. should timeout after 2 sec and return False.
    """
    assert not nettools.tcp_connection_test(ipaddr, port, timeout)
