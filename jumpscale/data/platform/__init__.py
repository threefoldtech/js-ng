"""This module helps with getting all of the information of the platform related to the machine hosting js-ng


## Get CPU count

```
JS-NG> j.data.platform.CPU_COUNT
4
```

## Check if 64-bit system

```
JS-NG> j.data.platform.IS_64BIT
True
```

## Check if linux or osx

```
JS-NG> j.data.platform.is_linux()
True

JS-NG> j.data.platform.is_osx()
False

JS-NG> j.data.platform.is_unix()
True

```

## Get linux info
```

JS-NG> j.data.platform.lsb_release_info()
{'distributor_id': 'Ubuntu', 'description': 'Ubuntu 18.04.4 LTS', 'release': '18.04', 'codename': 'bionic'}

JS-NG> j.data.platform.os_release_info()
{'name': 'Ubuntu', 'version': '18.04.4 LTS (Bionic Beaver)', 'id': 'ubuntu', 'id_like': 'debian', 'pretty_name': 'Ubuntu 18.04.4 LTS', 'version_id': '18.04', 'home_url': 'https://www.ubuntu.com/', 'support_url': 'https://help.ubuntu.com/', 'bug_report_url': 'https://bugs.launchpad.net/ubuntu/', 'privacy_policy_url': 'https://www.ubuntu.com/legal/terms-and-policies/privacy-policy', 'version_codename': 'bionic', 'ubuntu_codename': 'bionic', 'codename': 'bionic'}
JS-NG> j.data.platform.name
<function name at 0x7f267e1072f0>

JS-NG> j.data.platform.name()
'Ubuntu'


JS-NG> j.data.platform.main()
Name: Ubuntu 18.04.4 LTS
Version: 18.04 (bionic)
Codename: bionic
JS-NG> j.data.platform.version()
'18.04'
'Ubuntu 18.04.3 LTS', 'release': '18.04', 'codename': 'bionic'}

```

## Get python info

```
JS-NG> j.data.platform.get_python_info()
{'argv': 'jsng', 'bin': '/home/ahmed/.cache/pypoetry/virtualenvs/js-ng--jYQyIYz-py3.6/bin/python', 'version': '3.6.9 (default, Apr 18 2020, 01:56:04) [GCC 8.4.0]', 'compiler': 'GCC 8.4.0', 'build_date': 'Apr 18 2020 01:56:04', 'version_info': [3, 6, 9, 'final', 0], 'features': {'openssl': 'OpenSSL 1.1.1  11 Sep 2018', 'expat': 'expat_2.2.5', 'sqlite': '3.22.0', 'tkinter': '', 'zlib': '1.2.11', 'unicode_wide': True, 'readline': True, '64bit': True, 'ipv6': True, 'threading': True, 'urandom': True}}
```

## Get the complete profile info

```
JS-NG> j.data.platform.get_profile()
{'username': 'xmonader', 'guid': 'ce5a52d09920b248b602caf28539073', 'hostname': 'xmonader-ThinkPad-E580', 'hostfqdn': 'xmonader-Th
inkPad-E580', 'uname': {'system': 'Linux', 'node': 'xmonader-ThinkPad-E580', 'release': '4.15.0-55-generic', 'version': '#60-Ubunt
u SMP Tue Jul 2 18:22:20 UTC 2019', 'machine': 'x86_64', 'processor': 'x86_64'}, 'linux_dist_name': 'debian', 'linux_dist_version'
: 'buster/sid', 'cpu_count': 8, 'fs_encoding': 'utf-8', 'ulimit_soft': 1024, 'ulimit_hard': 1048576, 'cwd': '/home/xmonader/wspace
/threefoldtech/js-ng', 'umask': '0o2', 'python': {'argv': 'jsng', 'bin': '/home/xmonader/.cache/pypoetry/virtualenvs/js-ng-py3.7/bin/pyt
hon', 'version': '3.7.4 (default, Jul 12 2019, 20:57:46) [GCC 5.4.0 20160609]', 'compiler': 'GCC 5.4.0 20160609', 'build_date': 'J
ul 12 2019 20:57:46', 'version_info': [3, 7, 4, 'final', 0], 'features': {'openssl': 'OpenSSL 1.0.2s  28 May 2019', 'expat': 'expa
t_2.2.7', 'sqlite': '3.29.0', 'tkinter': '', 'zlib': '1.2.11', 'unicode_wide': True, 'readline': True, '64bit': True, 'ipv6': True
, 'threading': True, 'urandom': True}}, 'time_utc': '2019-08-18 11:24:23.636866', 'time_utc_offset': 2.0}

```
"""

# from boltons.ecoutils

import re
import os
import sys
import time
import pprint
import random
import socket
import struct
import getpass
import datetime
import platform

try:
    getrandbits = random.SystemRandom().getrandbits
    HAVE_URANDOM = True
except Exception:
    HAVE_URANDOM = False
    getrandbits = random.getrandbits


# 128-bit GUID just like a UUID, but backwards compatible to 2.4
INSTANCE_ID = hex(getrandbits(128))[2:-1].lower()

IS_64BIT = struct.calcsize("P") > 4
HAVE_UCS4 = getattr(sys, "maxunicode", 0) > 65536
HAVE_READLINE = True

try:
    import readline
except Exception:
    HAVE_READLINE = False

try:
    import sqlite3

    SQLITE_VERSION = sqlite3.sqlite_version
except Exception:
    # note: 2.5 and older have sqlite, but not sqlite3
    SQLITE_VERSION = ""


try:

    import ssl

    try:
        OPENSSL_VERSION = ssl.OPENSSL_VERSION
    except AttributeError:
        # This is a conservative estimate for Python <2.6
        # SSL module added in 2006, when 0.9.7 was standard
        OPENSSL_VERSION = "OpenSSL >0.8.0"
except Exception:
    OPENSSL_VERSION = ""


try:
    import Tkinter as tkinter

    TKINTER_VERSION = str(tkinter.TkVersion)
except Exception:
    TKINTER_VERSION = ""


try:
    import zlib

    ZLIB_VERSION = zlib.ZLIB_VERSION
except Exception:
    ZLIB_VERSION = ""


try:
    from xml.parsers import expat

    EXPAT_VERSION = expat.EXPAT_VERSION
except Exception:
    EXPAT_VERSION = ""


try:
    from multiprocessing import cpu_count

    CPU_COUNT = cpu_count()
except Exception:
    CPU_COUNT = 0

try:
    import threading

    HAVE_THREADING = True
except Exception:
    HAVE_THREADING = False


try:
    HAVE_IPV6 = socket.has_ipv6
except Exception:
    HAVE_IPV6 = False


try:
    from resource import getrlimit, RLIMIT_NOFILE

    RLIMIT_FDS_SOFT, RLIMIT_FDS_HARD = getrlimit(RLIMIT_NOFILE)
except Exception:
    RLIMIT_FDS_SOFT, RLIMIT_FDS_HARD = 0, 0


START_TIME_INFO = {"time_utc": str(datetime.datetime.utcnow()), "time_utc_offset": -time.timezone / 3600.0}


def get_python_info():
    ret = {}
    ret["argv"] = _escape_shell_args(sys.argv)
    ret["bin"] = sys.executable

    # Even though compiler/build_date are already here, they're
    # actually parsed from the version string. So, in the rare case of
    # the unparsable version string, we're still transmitting it.
    ret["version"] = " ".join(sys.version.split())

    ret["compiler"] = platform.python_compiler()
    ret["build_date"] = platform.python_build()[1]
    ret["version_info"] = list(sys.version_info)

    ret["features"] = {
        "openssl": OPENSSL_VERSION,
        "expat": EXPAT_VERSION,
        "sqlite": SQLITE_VERSION,
        "tkinter": TKINTER_VERSION,
        "zlib": ZLIB_VERSION,
        "unicode_wide": HAVE_UCS4,
        "readline": HAVE_READLINE,
        "64bit": IS_64BIT,
        "ipv6": HAVE_IPV6,
        "threading": HAVE_THREADING,
        "urandom": HAVE_URANDOM,
    }

    return ret


def get_profile(scrub=False):
    """The main entrypoint to platform. Calling this will return a
    JSON-serializable dictionary of information about the current
    process.
    It is very unlikely that the information returned will change
    during the lifetime of the process, and in most cases the majority
    of the information stays the same between runs as well.
    :func:`get_profile` takes one optional keyword argument, *scrub*,
    a :class:`bool` that, if True, blanks out identifiable
    information. This includes current working directory, hostname,
    Python executable path, command-line arguments, and
    username. Values are replaced with '-', but for compatibility keys
    remain in place.
    """
    ret = {}
    try:
        ret["username"] = getpass.getuser()
    except Exception:
        ret["username"] = ""
    ret["guid"] = str(INSTANCE_ID)
    ret["hostname"] = socket.gethostname()
    ret["hostfqdn"] = socket.getfqdn()
    uname = platform.uname()
    ret["uname"] = {
        "system": uname[0],
        "node": uname[1],
        "release": uname[2],  # linux: distro name
        "version": uname[3],  # linux: kernel version
        "machine": uname[4],
        "processor": uname[5],
    }
    try:
        linux_dist = platform.linux_distribution()
    except Exception:
        linux_dist = ("", "", "")
    ret["linux_dist_name"] = linux_dist[0]
    ret["linux_dist_version"] = linux_dist[1]
    ret["cpu_count"] = CPU_COUNT

    ret["fs_encoding"] = sys.getfilesystemencoding()
    ret["ulimit_soft"] = RLIMIT_FDS_SOFT
    ret["ulimit_hard"] = RLIMIT_FDS_HARD
    ret["cwd"] = os.getcwd()
    ret["umask"] = oct(os.umask(os.umask(2))).rjust(3, "0")

    ret["python"] = get_python_info()
    ret.update(START_TIME_INFO)

    if scrub:
        # mask identifiable information
        ret["cwd"] = "-"
        ret["hostname"] = "-"
        ret["hostfqdn"] = "-"
        ret["python"]["bin"] = "-"
        ret["python"]["argv"] = "-"
        ret["uname"]["node"] = "-"
        ret["username"] = "-"

    return ret


_real_safe_repr = pprint._safe_repr


def _fake_json_dumps(val, indent=2):
    # never do this. this is a hack for Python 2.4. Python 2.5 added
    # the json module for a reason.
    def _fake_safe_repr(*a, **kw):
        res, is_read, is_rec = _real_safe_repr(*a, **kw)
        if res == "None":
            res = "null"
        if res == "True":
            res = "true"
        if res == "False":
            res = "false"
        if not (res.startswith("'") or res.startswith("u'")):
            res = res
        else:
            if res.startswith("u"):
                res = res[1:]

            contents = res[1:-1]
            contents = contents.replace('"', "").replace(r"\"", "")
            res = '"' + contents + '"'
        return res, is_read, is_rec

    pprint._safe_repr = _fake_safe_repr
    try:
        ret = pprint.pformat(val, indent=indent)
    finally:
        pprint._safe_repr = _real_safe_repr

    return ret


def get_profile_json(indent=False):
    if indent:
        indent = 2
    else:
        indent = 0
    try:
        import json

        def dumps(val, indent):
            if indent:
                return json.dumps(val, sort_keys=True, indent=indent)
            return json.dumps(val, sort_keys=True)

    except ImportError:

        def dumps(val, indent):
            ret = _fake_json_dumps(val, indent=indent)
            if not indent:
                ret = re.sub("\n\s*", " ", ret)
            return ret

    data_dict = get_profile()
    return dumps(data_dict, indent)


def _escape_shell_args(args, sep=" ", style=None):
    if not style:
        if sys.platform == "win32":
            style = "cmd"
        else:
            style = "sh"

    if style == "sh":
        return _args2sh(args, sep=sep)
    elif style == "cmd":
        return _args2cmd(args, sep=sep)

    raise ValueError("style expected one of 'cmd' or 'sh', not %r" % style)


_find_sh_unsafe = re.compile(r"[^a-zA-Z0-9_@%+=:,./-]").search


def _args2sh(args, sep=" "):
    # see strutils
    ret_list = []

    for arg in args:
        if not arg:
            ret_list.append("''")
            continue
        if _find_sh_unsafe(arg) is None:
            ret_list.append(arg)
            continue
        # use single quotes, and put single quotes into double quotes
        # the string $'b is then quoted as '$'"'"'b'
        ret_list.append("'" + arg.replace("'", "'\"'\"'") + "'")

    return " ".join(ret_list)


def _args2cmd(args, sep=" "):
    # see strutils
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(" ")

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == "\\":
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append("\\" * len(bs_buf) * 2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return "".join(result)


def is_linux():
    return sys.platform.lower() == "linux"


def is_osx():
    return sys.platform.lower() == "darwin"


def is_unix():
    return is_linux() or is_osx()


if is_linux():
    from distro import *
