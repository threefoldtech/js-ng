"""
Docs for nettools

"""
# TODO: test *2

import time
import socket
import ipaddress
import re
from typing import Optional
from jumpscale.core.exceptions import Value, Runtime
import jumpscale.tools.http
import jumpscale.data.platform
import jumpscale.sals.fs
import jumpscale.core.executors
from jumpscale.data.types import IPAddress
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import ssl
import json


def tcp_connection_test(ipaddr: str, port: int, timeout: Optional[int] = None) -> bool:
    """tests tcp connection on specified port, compatible with both IPv4 and IPv6.
    ensures that each side of the connection is reachable in the network.

    Args:
        ipaddr (str): ip address or hostname
        port (int): port number
        timeout (int, optional): time before the connection test fails. Defaults to None.

    Returns:
        bool: True if the test succeeds, False otherwise
    """
    conn = None
    try:
        conn = socket.create_connection((ipaddr, port), timeout)
    except OSError as msg:
        return False
    finally:
        if conn:
            conn.close()
    return True


def udp_connection_test(ipaddr: str, port: int, timeout: Optional[int] = 1, message=b"PING") -> bool:
    """tests udp connection on specified port by sending specified message

    Args:
        ipaddr (str): ip address
        port (int): port number
        timeout (int, optional): time before the connection test fails. Defaults to None.
        message (str, optional): message to send. Defaults to b"PING"

    Returns:
        bool: True if the test succeeds, False otherwise
    """
    conn = socket.socket(type=socket.SOCK_DGRAM)
    if timeout:
        conn.settimeout(timeout)
    try:
        conn.connect((ipaddr, port))
    except BaseException:
        conn.close()
        return False

    conn.send(message)

    try:
        conn.recvfrom(8192)
    except Exception:
        return False
    return True


def wait_connection_test(ipaddr: str, port: int, timeout: Optional[int] = 5) -> bool:
    """Will wait until port listens on the specified address

    Args:
        ipaddr (str): ip address, or hostname
        port (int): port number
        timeout_total (int, optional): how long to wait for the connection. Defaults to 5.

    Returns:
        bool: True if the test succeeds, False otherwise
    """
    # port = int(port)
    deadline = time.time() + timeout
    while time.time() < deadline:
        if tcp_connection_test(ipaddr, port, timeout=2):
            return True
    return False


def wait_http_test(
    url: str, timeout: Optional[int] = 60, verify: Optional[bool] = True, interval_time: Optional[int] = 2
) -> bool:
    """Will keep try to reach specified url every {interval_time} sec until url become reachable or {timeout} elapsed

    Args:
        url (str): url
        timeout (int, optional): how long to keep trying to reach specified url. Defaults to 60.
        verify (bool, optional): boolean indication to verify the servers TLS certificate or not.
        interval_time (int, optional): how long to wait for a response before sending a new request. Defaults to 2.

    Returns:
        bool: true if the test succeeds
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        if check_url_reachable(url, interval_time, verify):
            return True
        # be gentle on system resource in case the above call to check_url_reachable() returned immediately (edge cases)
        time.sleep(1)
    return False


def check_url_reachable(
    url: str, timeout: Optional[int] = 5, verify: Optional[bool] = True, fake_user_agent: Optional[bool] = True
) -> bool:
    """Check that given url is reachable

    Args:
        url (str): url to test
        timeout (int, optional): timeout of test. Defaults to 5.
        verify (bool, optional): boolean indication to verify the servers TLS certificate or not.
        fake_user_agent (bool, optional): boolean indication to fake the user-agent and act like noraml browser or not.

    Raises:
        Input: raises if not correct url

    Returns:
        bool: True if the test succeeds, False otherwise
    """
    # fake the user-agent, to act like a normal browser
    # because some services will block requests from python default user-agent
    # ex: www.amazon.com, and it will looks unreachable to our code, unless we fake the user-agent.
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.1 Safari/603.1.30"
    }
    METHOD = "GET"

    if timeout:
        socket.setdefaulttimeout(timeout)

    context = None
    if not verify:
        # opt out of certificate verification on a single connection
        context = ssl._create_unverified_context()

    req = Request(url, headers=HEADERS if fake_user_agent else {}, method=METHOD)
    try:
        response = urlopen(req, timeout=timeout, context=context)
    except HTTPError as msg:
        # The server couldn't fulfill the request.
        status = msg.code
        return False
    except URLError as msg:
        # We failed to reach a server.
        return False
    except socket.timeout:
        return False
    else:
        status = response.code
        response.close()
        return status in range(200, 300)


def get_nic_names() -> list:
    """Get Nics on this machine

    Returns:
        list: list of all availabe nics
    """
    return [nic["name"] for nic in get_network_info()]


def get_nic_type(interface: str) -> str:
    """Get Nic Type on a certain interface

    Args:
        interface (str): interface name

    Raises:
        Runtime: if ethtool not installed on the system
        Value: if interface given is invalid

    Returns:
        str: type of the interface
    """
    output = ""
    if jumpscale.data.platform.is_linux():
        if jumpscale.sals.fs.exists(f"/sys/class/net/{interface}"):
            output = jumpscale.sals.fs.read_file(f"/sys/class/net/{interface}/type")
        if output.strip() == "32":
            return "INFINIBAND"
        else:
            if jumpscale.sals.fs.exists("/proc/net/vlan/%s" % (interface)):
                return "VLAN"
            exitcode, _, _ = jumpscale.core.executors.run_local("which ethtool", hide=True, warn=True)
            if exitcode != 0:
                raise Runtime("Ethtool is not installed on this system!")
            exitcode, output, _ = jumpscale.core.executors.run_local(f"ethtool -i {interface}", hide=True, warn=True)
            if exitcode != 0:
                return "VIRTUAL"
            match = re.search(r"^driver:\s+(?P<driver>\w+)\s*$", output, re.MULTILINE)
            if match and match.group("driver") == "tun":
                return "VIRTUAL"
            if match and match.group("driver") == "bridge":
                return "VLAN"
            return "ETHERNET_GB"

    elif jumpscale.data.platform.is_osx():
        command = f"ifconfig {interface}"
        exitcode, output, err = jumpscale.core.executors.run_local(command, hide=True, warn=True)
        if exitcode != 0:
            # temporary plumb the interface to lookup its mac
            jumpscale.core.executors.run_local(f"{command} plumb", hide=True)
            exitcode, output, err = jumpscale.core.executors.run_local(command, hide=True)
            jumpscale.core.executors.run_local(f"{command} unplumb", hide=True)
        if output.find("ipib") >= 0:
            return "INFINIBAND"
        else:
            # work with interfaces which are subnetted on vlans eq e1000g5000:1
            interfacepieces = interface.split(":")
            interface = interfacepieces[0]
            match = re.search(r"^\w+?(?P<interfaceid>\d+)$", interface, re.MULTILINE)
            if not match:
                raise Value(f"Invalid interface {interface}")
            if len(match.group("interfaceid")) >= 4:
                return "VLAN"
            else:
                if len(interfacepieces) > 1:
                    return "VIRTUAL"
                else:
                    return "ETHERNET_GB"


def get_reachable_ip_address(ip: str, port: Optional[int] = 0) -> str:
    """figures out what source address would be used if some traffic were to be sent out to specified ip.
    compatible with both IPv4 and IPv6.

    Args:
        ip (str): ip address
        port (int, optional): port number. does not matter much. No traffic is actually sent.

    Raises:
        ValueError: if address does not represent a valid IPv4 or IPv6 address.
        Runtime: if can't connect

    Returns:
        str: ip that can connect to the specified ip
    """
    try:
        ipaddr = ipaddress.ip_address(ip)
    except ValueError:
        raise
    if ipaddr.version == 4:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    else:  # create IPv6 socket when we connect to IPv6 address
        s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    try:
        s.connect((ip, port))
    except BaseException:
        raise Runtime("Cannot connect to %s:%s, check network configuration" % (ip, port))
    return s.getsockname()[0]


def get_default_ip_config(ip: Optional[str] = "8.8.8.8") -> tuple:
    """get default nic and address, by default, the one exposed to internet

    Args:
        ip (str): ip address. default to '8.8.8.8'

    Returns:
        tuple: default nic name and its ip address
    """
    ipaddr = get_reachable_ip_address(ip)
    for nic in get_network_info():
        for ipaddrv4, _ in nic["ip"]:
            if ipaddrv4 == ipaddr:
                return nic["name"], ipaddr
        for ipaddrv6, _ in nic["ip6"]:
            if ipaddrv6 == ipaddr:
                return nic["name"], ipaddr


def get_network_info(device: Optional[str] = None) -> list:
    """Get network info

    Args:
        device (str, optional): device name. Defaults to None.

    Raises:
        Runtime: if it could not find the specified device
        NotImplementedError: if the function runs on unsupported OS

    Returns:
        Dict, or list of dicts if device arg used: network info
        [{'ip': [('127.0.0.1', 8)], 'ip6': [('::1', 128)], 'mac': '00:00:00:00:00:00', 'name': 'lo'},
        {'ip': [('192.168.1.6', 24)],
         'ip6': [('fdb4:f58e:3c34:300:91f0:9c76:e1fb:d060', 64), ...],
         'mac': 'd8:9c:67:2a:f2:53',
         'name': 'wlp3s0'}, ...]
    """

    def _clean(nic_info: dict):
        result = {
            "ip": [(addr["local"], addr["prefixlen"]) for addr in nic_info["addr_info"] if addr["family"] == "inet"],
            "ip6": [(addr["local"], addr["prefixlen"]) for addr in nic_info["addr_info"] if addr["family"] == "inet6"],
            "mac": nic_info["address"],
            "name": nic_info["ifname"],
        }
        return result

    def _get_info(device: str):
        if not device:
            device = ""
        exitcode, output, _ = jumpscale.core.executors.run_local(f"ip -j addr show {device}", hide=True)
        if exitcode != 0:
            raise Runtime("could not find device")
        res = json.loads(output)

        for nic_info in res:
            yield _clean(nic_info)

    if jumpscale.data.platform.is_linux():
        if not device:
            res = []
            for nic in _get_info(device):
                res.append(nic)
            return res
        else:
            return list(_get_info(device))[0]
    else:
        # TODO: make it OSX Compatible
        raise NotImplementedError("this function supports only linux at the moment.")


def get_mac_address(interface: str) -> str:
    """Return the MAC address of this interface

    Args:
        interface (str): interface name

    Returns:
        str: mac of the interface
    """
    return get_network_info(interface)["mac"]


def get_host_name() -> str:
    """Get hostname of the machine

    Returns:
        str: host name
    """
    return socket.gethostname()


def is_nic_connected(interface: str) -> bool:
    """check if interface is connected

    Args:
        interface (str): interface name

    Returns:
        bool: whether it is connected or not
    """
    if jumpscale.data.platform.is_linux():
        carrierfile = f"/sys/class/net/{interface}/carrier"
        if not jumpscale.sals.fs.exists(carrierfile):
            return False
        try:
            return int(jumpscale.sals.fs.read_file(carrierfile)) != 0
        except IOError:
            return False

    elif jumpscale.data.platform.is_osx():
        command = f"dladm show-dev -p -o STATE {interface}"
        expectResults = ["up", "unknown"]

        exitcode, output, _ = jumpscale.core.executors.run_local(command, warn=True, hide=True)
        if exitcode != 0:
            return False
        output = output.strip()
        return output in expectResults


def get_host_by_name(dnsHostname: str) -> str:
    """get host address by its name

    Args:
        dnsHostname (str): host name

    Returns:
        str: host address
    """
    return socket.gethostbyname(dnsHostname)


def ping_machine(ip: str, timeout: Optional[int] = 60, allowhostname: Optional[bool] = True) -> bool:
    """Ping a machine to check if it's up/running and accessible

    Args:
        ip (str): Machine Ip Address
        pingtimeout (int, optional): time in sec after which ip will be declared as unreachable. Defaults to 60.
        allowhostname (bool, optional): allow pinging on hostname. Defaults to True.

    Raises:
        Value: if ip is Invalid ip address
        NotImplementedError: if the function runs on unsupported system

    Returns:
        bool: True if machine is pingable, False otherwise
    """
    if not allowhostname:
        if not IPAddress().check(ip):
            raise Value("Invalid ip address, set allowhostname to use hostnames")

    if jumpscale.data.platform.is_linux():
        exitcode, _, _ = jumpscale.core.executors.run_local(f"ping -c 1 -w {timeout} {ip}", warn=True, hide=True)
    elif jumpscale.data.platform.is_osx():
        exitcode, _, _ = jumpscale.core.executors.run_local(f"ping -o -t {timeout} {ip}", warn=True, hide=True)
    else:  # unsupported platform
        raise NotImplementedError("Not Implemented for this os")
    return exitcode == 0


def download(
    url: str,
    localpath: str,
    username: Optional[str] = None,
    passwd: Optional[str] = None,
    overwrite: Optional[bool] = True,
):
    """Download a url to a file or a directory, supported protocols: http, https, ftp, file
    @param url: URL to download from
    @type url: string
    @param localpath: filename or directory to download the url to pass - to return data
    @type localpath: string
    @param username: username for the url if it requires authentication
    @type username: string
    @param passwd: password for the url if it requires authentication
    @type passwd: string
    """
    if not url:
        raise Value("URL can not be None or empty string")
    if not localpath:
        raise Value("Local path to download the url to can not be None or empty string")
    filename = ""
    if localpath == "-":
        filename = "-"
    if jumpscale.sals.fs.exists(localpath) and jumpscale.sals.fs.is_dir(localpath):
        filename = jumpscale.sals.fs.join_paths(localpath, jumpscale.sals.fs.basename(url))
    else:
        if jumpscale.sals.fs.is_dir(jumpscale.sals.fs.dirname(localpath)):
            filename = localpath
        else:
            raise Value("Local path is an invalid path")

    if not jumpscale.sals.fs.exists(filename):
        overwrite = True

    if overwrite:
        if username and passwd and jumpscale.tools.http.urllib3.util.parse_url(url).scheme == "ftp":
            url = url.split("://")[0] + "://%s:%s@" % (username, passwd) + url.split("://")[1]
        response = jumpscale.tools.http.get(
            url, stream=True, auth=jumpscale.tools.http.auth.HTTPBasicAuth(username, passwd)
        )
        response.raise_for_status()
        if filename != "-":
            with open(filename, "wb") as fw:
                for chunk in response.iter_content(chunk_size=2048):
                    if chunk:  # filter out keep-alive new chunks
                        fw.write(chunk)
            return
        else:
            return response.content


def _netobject_get(device: str) -> ipaddress.IPv4Network:
    n = get_network_info(device)
    net = ipaddress.IPv4Network(n["ip"][0][0] + "/" + str(n["ip"][0][1]), strict=False)
    return net


def netrange_get(device: str, skip_begin: Optional[int] = 10, skip_end: Optional[int] = 10) -> tuple:
    """
    Get ($fromip,$topip) from range attached to device, skip the mentioned ip addresses.

    :param device: device name
    :type device: str
    :param skip_begin: ips to skip from the begining of the range, defaults to 10
    :type skip_begin: int, optional
    :param skip_end: ips to skip from the end of the range, defaults to 10
    :type skip_end: int, optional

    :return: ip range for this device
    :rtype: tuple
    """
    n = _netobject_get(device)
    return (str(n[0] + skip_begin), str(n[-1] - skip_end))
