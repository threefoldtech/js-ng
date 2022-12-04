"""This module contains a collection of functions which help in manage network connections and interfaces.

General Note on python socket operations:
    If you use a hostname in the host portion of IPv4/v6 socket address,the program may show a nondeterministic behavior,
    as Python uses the first address returned from the DNS resolution. The socket address will be resolved differently
    into an actual IPv4/v6 address, depending on the results from DNS resolution and/or the host configuration.
    For deterministic behavior use a numeric address in host portion.
    https://docs.python.org/3/library/socket.html
"""
import time
import socket
import ipaddress
import re
import ssl
import json
import subprocess
import shutil
from os.path import basename
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse
from urllib.request import build_opener, HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler, install_opener
from pathlib import Path
from collections import namedtuple
from jumpscale.loader import j
from jumpscale.core.exceptions import Value, Runtime
import jumpscale.tools.http
import jumpscale.data.platform
import jumpscale.sals.fs
import jumpscale.core.executors


def tcp_connection_test(ipaddr: str, port: int, timeout: Optional[int] = None) -> bool:
    """tests tcp connection on specified port, compatible with both IPv4 and IPv6.
    ensures that each side of the connection is reachable in the network.

    Raises:
        socket.gaierror: raised for address-related errors.
        socket.herror: raised for address-related errors.

    Args:
        ipaddr (str): ip address or hostname
        port (int): port number
        timeout (int, optional): time before the connection test fails. Defaults to None.

    Returns:
        bool: True if the test succeeds, False otherwise
    """
    try:
        with socket.create_connection((ipaddr, port), timeout) as conn:
            return True
    except (ConnectionRefusedError, socket.timeout, OSError):
        return False


def udp_connection_test(ipaddr: str, port: int, timeout: Optional[int] = 1, message: Optional[bytes] = b"") -> bool:
    """tests udp connection on specified port by sending specified message and expecting
    to receive at least one byte from the socket as an indicator of connection success

    Args:
        ipaddr (str): ip address
        port (int): port number
        timeout (int, optional): time before the connection test fails. Defaults to None.
        message (str, optional): message to send. Defaults to b"PING"

    Raises:
        ValueError: raises if invalid ip address was used

    Returns:
        bool: True if the test succeeds, False otherwise
    """
    ip = ipaddress.ip_address(ipaddr)
    if ip.version == 4:
        family = socket.AF_INET
    else:
        family = socket.AF_INET6

    with socket.socket(family, socket.SOCK_DGRAM) as sock:
        if timeout:
            sock.settimeout(timeout)

        try:
            sock.sendto(message, (ipaddr, port))
            # expecting to receive at least one byte from the socket as indication to succeed connection
            data, _ = sock.recvfrom(1)
            return True
        except (socket.timeout, OSError):
            return False


def wait_connection_test(ipaddr: str, port: int, timeout: Optional[int] = 6) -> bool:
    """Will wait until port listens on the specified address or `timeout` sec elapsed

    under the hood the function will try to connect every `interval` sec, if waiting time `timeout` set
    to value <= 2, `interval` is 1 sec, otherwise 2.

    Args:
        ipaddr (str): ip address, or hostname
        port (int): port number
        timeout_total (int, optional): how long to wait for the connection. if the timeout set to value > 2,
            due to the way the function works, it makes sense to choose an even number. Defaults to 6.

    Returns:
        bool: True if the test succeeds, False otherwise
    """
    # port = int(port)
    interval = 1 if timeout <= 2 else 2
    init_start = time.time()
    deadline = init_start + timeout
    while time.time() < deadline:
        start = time.time()
        if tcp_connection_test(ipaddr, port, timeout=interval):
            return True
        # if return immediately (err111) take a break before retry
        if time.time() - start < interval:
            time.sleep(1)
    return False


def wait_http_test(
    url: str, timeout: Optional[int] = 60, verify: Optional[bool] = True, interval_time: Optional[int] = 2
) -> bool:
    """Will keep try to reach specified url every {interval_time} sec until url become reachable or {timeout} sec elapsed

    Args:
        url (str): url
        timeout (int, optional): how long to keep trying to reach specified url. Defaults to 60.
        verify (bool, optional): boolean indication to verify the servers TLS certificate or not.
        interval_time (int, optional): how long to wait for a response before sending a new request. Defaults to 2.

    Raises:
        ValueError: raises if not correct url

    Returns:
        bool: true if the test succeeds
    """
    init_start = time.time()
    deadline = init_start + timeout
    while time.time() < deadline:
        start = time.time()
        if check_url_reachable(url, interval_time, verify):
            return True
        # be gentle on system resource in case the above call to check_url_reachable() returned immediately (edge cases)
        if time.time() - start < interval_time:
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
        fake_user_agent (bool, optional): boolean indication to fake the user-agent and act like normal browser or not.

    Raises:
        ValueError: raises if not correct url

    Returns:
        bool: True if the test succeeds, False otherwise
    """
    # fake the user-agent, to act like a normal browser
    # because some services will block requests from python default user-agent
    # By default urllib identifies itself as Python-urllib/x.y (e.g. Python-urllib/2.5),
    # which may confuse the site, or just plain not work.
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
        with urlopen(req, timeout=timeout, context=context):
            return True
    except (HTTPError, URLError, socket.timeout):
        return False


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
        port (int, optional): port number. does not matter much. No traffic is actually sent. Defaults to 0.

    Raises:
        ValueError: if address does not represent a valid IPv4 or IPv6 address, or port is invalid.
        RuntimeError: if can't connect

    Returns:
        str: ip that can connect to the specified ip
    """
    ipaddr = ipaddress.ip_address(ip)

    if ipaddr.version == 4:
        family = socket.AF_INET
    else:
        family = socket.AF_INET6

    with socket.socket(family, socket.SOCK_DGRAM) as sock:
        try:
            sock.connect((ip, port))
        except OSError as e:
            # (ConnectionRefusedError, socket.timeout, socket.herror, socket.gaierror)
            reason = e.error if hasattr(e, "error") else repr(e)
            raise RuntimeError(f"Cannot connect to {ip}:{port} because of this error: {reason}")
        except (ValueError, TypeError, OverflowError) as e:
            # incorrect port numper or type
            raise ValueError(repr(e))

        return sock.getsockname()[0]


def get_default_ip_config(ip: Optional[str] = "8.8.8.8") -> tuple:
    """get default nic and address, by default, the one exposed to internet

    Args:
        ip (str): ip address. default to '8.8.8.8'

    Raises:
        ValueError: if address does not represent a valid IPv4 or IPv6 address.
        RuntimeError: if can't connect

    Returns:
        tuple: default nic name and its ip address
    """
    ipaddr = ipaddress.ip_address(ip)
    address_family = "ip" if ipaddr.version == 4 else "ip6"
    source_addr = get_reachable_ip_address(ip)
    default_nic = None
    for nic in get_network_info():
        for candidate_ip, _ in nic[address_family]:
            if candidate_ip == source_addr:
                default_nic = (nic["name"], source_addr)
                break
        if default_nic is not None:
            break
    return default_nic


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

    def _get_info():
        if device:
            # exitcode, output, _ = jumpscale.core.executors.run_local(f"ip -j addr show {device}", hide=True, warn=True)
            # if exitcode != 0:
            #    raise Runtime("could not find device")
            try:
                output = subprocess.check_output(f"ip -j addr show {device}", shell=True)
            except subprocess.CalledProcessError as e:
                # the process returns a non-zero exit status.
                # This probably happened because specified interface name does not exists
                j.logger.exception(f"cmd: {e.cmd} returns a non-zero exit status.", exception=e)
                raise RuntimeError(f"could not find this interface: {device}")
        else:
            # _, output, _ = jumpscale.core.executors.run_local("ip -j addr show", hide=True, warn=True)
            output = subprocess.check_output("ip -j addr show", shell=True)
        res = json.loads(output)
        for nic_info in res:
            # when use ip command with -j option and specified interface. it returns on ubuntu < 20
            # a list contains a requested info alongside other partially empty dicts like this -> {'addr_info': [{}, {}]}
            # so we need to filter those dicts to get consistent behavior at all supported ubuntu versions.
            if len(nic_info) > 1:
                yield _clean(nic_info)
            else:
                j.logger.debug(f"Discarded this improper json\n{nic_info}")
                continue

    if jumpscale.data.platform.is_linux():
        if not device:
            res = []
            for nic in _get_info():
                res.append(nic)
            return res
        else:
            return next(_get_info())

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


def get_host_name() -> str:  # pragma: no cover - we're just proxying
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
        try:
            is_up = int(jumpscale.sals.fs.read_file(carrierfile)) != 0
            return is_up
        except IOError as e:
            j.logger.exception(e.strerror or repr(e), exception=e)
            return False

    elif jumpscale.data.platform.is_osx():
        # superuser.com/questions/203272/
        command = "ifconfig -{} | sed -E 's/[[:space:]:].*//;/^$/d"
        option = {"up": "u", "down": "d"}
        stdout = subprocess.check_output(command.format(option["up"]), shell=True)
        output = stdout.decode("utf-8")
        up_interfaces = output.split()
        return interface in up_interfaces


def get_host_by_name(dnsHostname: str) -> str:  # pragma: no cover - we're just proxying
    """get host address by its name

    Args:
        dnsHostname (str): host name

    Returns:
        str: host address
    """
    return socket.gethostbyname(dnsHostname)


def ping_machine(ip: str, timeout: Optional[int] = 60, allowhostname: Optional[bool] = True) -> bool:
    """Ping a machine to check if it's up/running and accessible
    Note: Any well-behaved device on an LAN or WAN is free to ignore nearly any traffic,
    so PINGs, port scans, and the like are all unreliable.

    Args:
        ip (str): Machine Ip Address
        pingtimeout (int, optional): time in sec after which ip will be declared as unreachable. Defaults to 60.
        allowhostname (bool, optional): allow pinging on hostname. Defaults to True.

    Raises:
        ValueError: if ip is Invalid ip address
        NotImplementedError: if the function runs on unsupported system

    Returns:
        bool: True if machine is pingable, False otherwise
    """
    if not allowhostname:
        ipaddress.ip_address(ip)

    if jumpscale.data.platform.is_linux():
        try:
            _ = subprocess.check_output(f"ping -c 1 -w {timeout} {ip}", shell=True)
            exitcode = 0
        except subprocess.CalledProcessError as e:
            exitcode = e.returncode
        # exitcode, output, err = jumpscale.core.executors.run_local(f"ping -c 1 -w {timeout} {ip}", warn=True, hide=True)
    elif jumpscale.data.platform.is_osx():
        try:
            _ = subprocess.check_output(f"ping -o -t {timeout} {ip}", shell=True)
            exitcode = 0
        except subprocess.CalledProcessError as e:
            exitcode = e.returncode
        # exitcode, _, _ = jumpscale.core.executors.run_local(f"ping -o -t {timeout} {ip}", warn=True, hide=True)
    else:  # unsupported platform
        raise NotImplementedError("Not Implemented for this os")
    return exitcode == 0


def download(
    url: str,
    localpath: Optional[str] = "",
    username: Optional[str] = None,
    passwd: Optional[str] = None,
    overwrite: Optional[bool] = True,
    append_to_home: Optional[bool] = False,
    name_from_url: Optional[bool] = True,
):
    """Download a url to a file or a directory, supported protocols: http, https, ftp, file

    Args:
        url (str): URL to download from
        localpath (str): filename or directory to download the url to. pass None to return the data. Defaults to ''.
        username (str, optional): username for the url if it requires authentication. Defaults to None.
        passwd (str, optional): password for the url if it requires authentication. Defaults to None.
        overwrite (bool, optional): if the file exists, it will be truncated. Defaults to True.
        append_to_home (bool, optional): if set to true, any relative path specified in localpath arg
            will be appended to the user home directory (that guaranteed to have a write permission). if set
            to False any relative localpath set by user will append to the current working directory. if user
            specified a absolute localpath (start with /) append_to_home will have no effect. Defaults to False.
        name_from_url (bool, optional): if set to true, localpath will treated as a dir, and will try to get
            the file name from the url or fallback to auto generated name. Defaults to True.

    Raises:
        PermissionError: [description]
        FileNotFoundError: [description]
        FileExistsError: [description]
        ValueError: [description]
        URLError: [description]

    Returns:
        namedtuple: namedtuple('DownloadResult', ['localpath', 'content', content_length])
            - localpath (pathlib.Path)
            - content (bytes): only if localpath is None else it will be None always
            - content_length: the content length as returned from the response headers

    Todo:
        - better performance with Multi-Threaded
        - support resume

    Examples:
        # use default values for args will download the url to cwd and get the name from the url,
        # if the file already exists, it will overwritten.
        >>> nettools.download('https://www.7-zip.org/a/7z1900-extra.7z')
        DownloadResult(localpath=PosixPath('/home/sameh/projects/js-ng/7z1900-extra.7z'), content=None, content_length='929117')

    """
    DownloadResult = namedtuple("DownloadResult", ["localpath", "content", "content_length"])
    file_name = ""

    try:
        parsed_url = urlparse(url)
    except ValueError as e:
        j.logger.exception(repr(e), exception=e)
        raise

    if name_from_url:
        file_name = basename(parsed_url.path)  # TODO: insure safe file name and fall back if can't get the file name
    elif localpath == "":
        j.logger.error(f"Improper args used.\nname_from_url: {name_from_url}\nlocalpath: {localpath}")
        raise ValueError("localpath can't be empty when name_from_url is False")

    if username and passwd:
        if parsed_url.scheme == "ftp":
            url = "ftp://%s:%s@" % (username, passwd) + url.split("://")[1]
        elif parsed_url.scheme in ("http", "https"):
            # create a password manager
            password_mgr = HTTPPasswordMgrWithDefaultRealm()
            # Add the username and password.
            # If we knew the realm, we could use it instead of None.
            password_mgr.add_password(None, parsed_url.netloc, username, passwd)
            handler = HTTPBasicAuthHandler(password_mgr)
            # create "opener" (OpenerDirector instance)
            opener = build_opener(handler)
            install_opener(opener)

    req = Request(url)
    req.add_header(
        "User-agent",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
    )

    try:
        response = urlopen(req)
        content_length = response.headers.get("Content-Length")
    except URLError as e:
        if hasattr(e, "reason"):
            msg = "We failed to reach a server."
            msg += " Reason: " + e.reason
        elif hasattr(e, "code"):
            msg = "The server couldn't fulfill the request."
            msg += " Error code: " + e.code
        j.logger.exception(msg, exception=e)
        raise

    if localpath is None:
        return DownloadResult(localpath=None, content=response.read(), content_length=content_length)

    file_path = Path(localpath) / file_name
    if not file_path.is_absolute() and append_to_home:
        file_path = Path.home() / file_path

    dir_path = file_path.parent

    try:
        dir_path.mkdir(parents=True, exist_ok=True)
    except (PermissionError, FileNotFoundError) as e:
        j.logger.exception(e.strerror or repr(e), exception=e)
        raise

    if overwrite:
        file_mode = "wb"  # if exists will truncated
    else:
        file_mode = "xb"  # if exists will raise exception

    try:
        with file_path.open(file_mode) as f_handler:
            shutil.copyfileobj(response, f_handler, length=8 * 1024 * 1024)
            return DownloadResult(localpath=file_path.resolve(), content=None, content_length=content_length)
    finally:
        response.close()


def _netobject_get(device: str) -> ipaddress.IPv4Network:
    n = get_network_info(device)
    net = ipaddress.IPv4Network(n["ip"][0][0] + "/" + str(n["ip"][0][1]), sdirnametrict=False)
    return net


def netrange_get(device: str, skip_begin: Optional[int] = 10, skip_end: Optional[int] = 10) -> tuple:
    """Get ($fromip,$topip) from range attached to device, skip the mentioned ip addresses.

    Args:
        device (str): [description]
        skip_begin (Optional[int], optional): ips to skip from the begining of the range, Defaults to 10.
        skip_end (Optional[int], optional): ips to skip from the end of the range, Defaults to 10.

    Returns:
        tuple: ip range for this device
    """
    n = _netobject_get(device)
    return (str(n[0] + skip_begin), str(n[-1] - skip_end))


def get_free_port(ipv6: Optional[bool] = False, udp: Optional[bool] = False, return_socket: Optional[bool] = False):
    """Bind an ipv4 or ipv6 socket to port 0 to make OS pick a random, free and
    available port from 1024 to 65535.

    you can optionally choose to reuse the socket by set return_socket to True (preferred to
    To prevent race conditions from occurring) but then it is your responsibility to close
    that socket calling its close method after you finish with it to free the selected port.
    by default you got tcp port, but setting udp to True will set socket type to UDP.

    Args:
        ipv6 (bool, optional): weather to bind the free port to 127.0.0.1 or ::1. Defaults to False.
        udp (bool, optional): set socket type to udp instead of tcp. Defaults to False.
        return_socket (bool, optional): return the socket alongside the port to reuse it. Defaults to False.

    Returns:
        int: returns a random free port from 1024 to 65535 range.
        Optional[socket]: in the case of return_socket set to True, socket will be returned alongside the port in a tuple.

    Example:
        # get a free TCP port that currently not binded to 127.0.0.1
        >>> port = get_free_port()
        # get a free UDP port that currently not binded to 127.0.0.1
        >>> port = get_free_port(udp=True)
        # get a free TCP port that currently not binded to ::1
        >>> port = get_free_port(ipv6=True)
        # get a free TCP port that currently not binded to 127.0.0.1
        # and reuse the socket instead of creating a socket and bind it to selected port
        >>> port, sock = get_free_port(return_socket=True)
        >>> sock.listen()
        ..
        >>> sock.close()
    """
    socket_type = socket.SOCK_DGRAM if udp else socket.SOCK_STREAM
    # Picking a random port is not a good idea - let the OS pick one for you.
    if ipv6:
        sock = socket.socket(socket.AF_INET6, socket_type)
        sock.bind(("::1", 0))
    else:
        sock = socket.socket(socket.AF_INET, socket_type)
        sock.bind(("127.0.0.1", 0))

    # retrieve the selected port with getsockname() right after bind()
    port = sock.getsockname()[1]
    # returns port or (port, socket) depend on the bool value of return_socket
    return (port, sock) if return_socket else port
