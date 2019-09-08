# TODO: test *2

import time
import socket
import ipaddress
import re
import os
from typing import Optional
from jumpscale.god import j


def tcp_connection_test(ipaddr: str, port: int, timeout: Optional[int]):
    """tests tcp connection on specified port

    Args:
        ipaddr (str): ip address
        port (int): port number
        timeout (int, optional): time before the connection test fails. Defaults to None.

    Returns:
        bool: True if the test succeeds, False otherwise
    """
    conn = None
    try:
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if timeout:
            conn.settimeout(timeout)
        try:
            conn.connect((ipaddr, port))
        except BaseException:
            return False
    finally:
        if conn:
            conn.close()
    return True


def udp_connection_test(ipaddr: str, port: int, timeout=1, message=b"PING"):
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

    j.logger.info(f"Sending {len(message)} bytes to {ipaddr}:{port}")
    conn.send(message)

    try:
        conn.recvfrom(8192)
    except Exception:
        return False
    return True


def wait_connection_test(ipaddr: str, port: int, timeout=5):
    """Will wait until port listens on the specified address

    Args:
        ipaddr (str): ip address
        port (int): port number
        timeout_total (int, optional): how long to wait for the connection. Defaults to 5.

    Returns:
        bool: True if the test succeeds, False otherwise
    """
    port = int(port)
    end = j.data.time.now().timestamp + timeout
    while True:
        if j.data.time.now().timestamp > end:
            return False
        if tcp_connection_test(ipaddr, port, timeout=2):
            return True


def check_url_reachabel(url: str, timeout=5):
    """Check that given url is reachable

    Args:
        url (str): url to test
        timeout (int, optional): timeout of test. Defaults to 5.

    Raises:
        j.exceptions.Input: raises if not correct url

    Returns:
        bool: True if the test succeeds, False otherwise
    """
    try:
        code = j.tools.http.get(url, timeout=timeout).status_code
        return code == 200
    except j.tools.http.exceptions.MissingSchema:
        raise j.exceptions.Input("Please specify correct url with correct scheme")
    except j.tools.http.exceptions.ConnectionError:
        return False


def get_nic_names():
    """Get Nics on this machine

    Returns:
        list: list of all availabe nics
    """
    return [nic["name"] for nic in get_network_info()]


def get_nic_type(interface):
    """Get Nic Type on a certain interface

    Args:
        interface (str): interface name

    Raises:
        j.exceptions.Runtime: if ethtool not installed on the system
        j.exceptions.Value: if interface given is invalid

    Returns:
        str: type of the interface
    """
    output = ""
    if j.data.platform.is_linux():
        if j.sals.fs.exists(f"/sys/class/net/{interface}"):
            output = j.sals.fs.read_file(f"/sys/class/net/{interface}/type")
        if output.strip() == "32":
            return "INFINIBAND"
        else:
            if j.sals.fs.exists("/proc/net/vlan/%s" % (interface)):
                return "VLAN"
            exitcode, _, _ = j.core.executors.run_local("which ethtool", hide=True, warn=True)
            if exitcode != 0:
                raise j.exceptions.Runtime("Ethtool is not installed on this system!")
            exitcode, output, _ = j.core.executors.run_local(f"ethtool -i {interface}", hide=True, warn=True)
            if exitcode != 0:
                return "VIRTUAL"
            match = re.search(r"^driver:\s+(?P<driver>\w+)\s*$", output, re.MULTILINE)
            if match and match.group("driver") == "tun":
                return "VIRTUAL"
            if match and match.group("driver") == "bridge":
                return "VLAN"
            return "ETHERNET_GB"

    elif j.data.platform.is_osx():
        command = f"ifconfig {interface}"
        exitcode, output, err = j.core.executors.run_local(command, hide=True, warn=True)
        if exitcode != 0:
            # temporary plumb the interface to lookup its mac
            j.logger.info(
                f"Interface {interface} is down. Temporarily plumbing it to be able to lookup its nic type"
            )
            j.core.executors.run_local(f"{command} plumb", hide=True)
            exitcode, output, err = j.core.executors.run_local(command, hide=True)
            j.core.executors.run_local(f"{command} unplumb", hide=True)
        if output.find("ipib") >= 0:
            return "INFINIBAND"
        else:
            # work with interfaces which are subnetted on vlans eq e1000g5000:1
            interfacepieces = interface.split(":")
            interface = interfacepieces[0]
            match = re.search(r"^\w+?(?P<interfaceid>\d+)$", interface, re.MULTILINE)
            if not match:
                raise j.exceptions.Value(f"Invalid interface {interface}")
            if len(match.group("interfaceid")) >= 4:
                return "VLAN"
            else:
                if len(interfacepieces) > 1:
                    return "VIRTUAL"
                else:
                    return "ETHERNET_GB"


def get_reachable_ip_address(ip: str, port: int):
    """Returns the first local ip address that can connect to the specified ip on the specified port

    Args:
        ip (str): ip address
        port (int): port number

    Raises:
        j.exceptions.RuntimeError: if can't connect

    Returns:
        str: ip that can connect to the specified ip
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((ip, port))
    except BaseException:
        raise j.exceptions.RuntimeError("Cannot connect to %s:%s, check network configuration" % (ip, port))
    return s.getsockname()[0]


def get_default_ip_config():
    """get default nic and address

    Returns:
        tuple: default nic and address
    """
    ipaddr = get_reachable_ip_address("8.8.8.8", 22)
    for item in get_network_info():
        for ipaddr2 in item["ip"]:
            # print "%s %s"%(ipaddr2,ipaddr)
            if str(ipaddr) == str(ipaddr2):
                return item["name"], ipaddr


def get_network_info(device=None):
    """
    Get network info

    [{'cidr': 8, 'ip': ['127.0.0.1'], 'mac': '00:00:00:00:00:00', 'name': 'lo'},
        {'cidr': 24,
        'ip': ['192.168.0.105'],
        'ip6': ['...','...],
        'mac': '80:ee:73:a9:19:05',
        'name': 'enp2s0'},
        {'cidr': 0, 'ip': [], 'mac': '80:ee:73:a9:19:06', 'name': 'enp3s0'},
        {'cidr': 16,
        'ip': ['172.17.0.1'],
        'mac': '02:42:97:63:e6:ba',
        'name': 'docker0'}]

    :param device: device name, defaults to None
    :type device: str, optional
    :raises RuntimeError: if the platform isn't implemented
    :return: network info
    :rtype: list or dict if device is specified
    """
    IPBLOCKS = re.compile(r"(^|\n)(?P<block>\d+:.*?)(?=(\n\d+)|$)", re.S)
    IPMAC = re.compile(r"^\s+link/\w+\s+(?P<mac>(\w+:){5}\w{2})", re.M)
    IPIP = re.compile(r"\s+?inet\s(?P<ip>(\d+\.){3}\d+)/(?P<cidr>\d+)", re.M)
    IPNAME = re.compile(r"^\d+: (?P<name>.*?)(?=:)", re.M)

    def block_parse(block):
        result = {"ip": [], "ip6": [], "cidr": [], "mac": "", "name": ""}
        for rec in (IPMAC, IPNAME):
            match = rec.search(block)
            if match:
                result.update(match.groupdict())
        for mrec in (IPIP,):
            for m in mrec.finditer(block):
                for key, value in list(m.groupdict().items()):
                    result[key].append(value)
        _, IPV6, _ = j.core.executors.run_local("ifconfig %s |  awk '/inet6/{print $2}'" % result["name"], hide=True)
        for ipv6 in IPV6.split("\n"):
            result["ip6"].append(ipv6)
        if isinstance(result["cidr"], list):
            if len(result["cidr"]) == 0:
                result["cidr"] = 0
            else:
                result["cidr"] = int(result["cidr"][0])
        return result

    def networkinfo_get():
        _, output, _ = j.core.executors.run_local("ip a", hide=True)
        for m in IPBLOCKS.finditer(output):
            block = m.group("block")
            yield block_parse(block)

    res = []
    for nic in networkinfo_get():
        if nic["name"] == device:
            return nic
        res.append(nic)

    if device is not None:
        raise j.exceptions.Runtime("could not find device")
    return res


def get_mac_address(interface: str):
    """Return the MAC address of this interface

    Args:
        interface (str): interface name

    Returns:
        str: mac of the interface
    """
    return get_network_info(interface)["mac"]


def get_host_name():
    """Get hostname of the machine

    Returns:
        str: host name
    """
    return socket.gethostname()


def is_nic_connected(interface: str):
    """check if interface is connected

    Args:
        interface (str): interface name

    Returns:
        bool: whether it is connected or not
    """
    if j.data.platform.is_linux():
        carrierfile = f"/sys/class/net/{interface}/carrier"
        if not j.sals.fs.exists(carrierfile):
            return False
        try:
            return int(j.sals.fs.read_file(carrierfile)) != 0
        except IOError:
            return False

    elif j.data.platform.is_osx():
        command = f"dladm show-dev -p -o STATE {platform}"
        expectResults = ["up", "unknown"]

        exitcode, output, _ = j.core.executors.run_local(command, warn=True, hide=True)
        if exitcode != 0:
            return False
        output = output.strip()
        return output in expectResults


def get_host_by_name(dnsHostname: str):
    """get host address by its name

    Args:
        dnsHostname (str): host name

    Returns:
        str: host address
    """
    return socket.gethostbyname(dnsHostname)


def ping_machine(ip, pingtimeout=60, allowhostname=True):
    """Ping a machine to check if it's up/running and accessible
    @param ip: Machine Ip Address
    @param pingtimeout: time in sec after which ip will be declared as unreachable
    @param allowhostname: allow pinging on hostname (default is false)
    @rtype: True if machine is pingable, False otherwise
    """
    if not allowhostname:
        if not j.data.types.IPAddress().check(ip):
            raise j.exceptions.Value("Invalid ip address, set allowedhostname to use hostnames")

    start = time.time()
    pingsucceeded = False
    while time.time() - start < pingtimeout:
        if j.data.platform.is_linux():
            # ping -c 1 -W 1 IP
            exitcode, _, _ = j.core.executors.run_local(f"ping -c 1 -W 1 -w 1 {ip}", warn=True, hide=True)
        elif j.data.platform.is_osx():
            exitcode, _, _ = j.core.executors.run_local(f"ping -c 1 {ip}", warn=True, hide=True)
        if exitcode == 0:
            pingsucceeded = True
            return True
        time.sleep(1)
    if not pingsucceeded:
        return False


def download(url, localpath, username=None, passwd=None, overwrite=True):
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
        raise j.exceptions.Value("URL can not be None or empty string")
    if not localpath:
        raise j.exceptions.Value("Local path to download the url to can not be None or empty string")
    filename = ""
    if localpath == "-":
        filename = "-"
    if j.sals.fs.exists(localpath) and j.sals.fs.is_dir(localpath):
        filename = j.sals.fs.join_paths(localpath, j.sals.fs.basename(url))
    else:
        if j.sals.fs.is_dir(j.sals.fs.dirname(localpath)):
            filename = localpath
        else:
            raise j.exceptions.Value("Local path is an invalid path")

    if not j.sals.fs.exists(filename):
        overwrite = True

    if overwrite:
        if username and passwd and j.tools.http.urllib3.util.parse_url(url).scheme == "ftp":
            url = url.split("://")[0] + "://%s:%s@" % (username, passwd) + url.split("://")[1]
        response = j.tools.http.get(url, stream=True, auth=j.tools.http.auth.HTTPBasicAuth(username, passwd))
        response.raise_for_status()
        if filename != "-":
            with open(filename, "wb") as fw:
                for chunk in response.iter_content(chunk_size=2048):
                    if chunk:  # filter out keep-alive new chunks
                        fw.write(chunk)
            return
        else:
            return response.content
    j.logger.info("!!! File already exists did not overwrite")


def _netobject_get(device: str):
    n = get_network_info(device)
    net = ipaddress.IPv4Network(n["ip"][0] + "/" + str(n["cidr"]), strict=False)
    return net


def netrange_get(device, skip_begin=10, skip_end=10):
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
