# j.data.platform

This module helps with getting all of the information of the platform related to the machine hosting js-ng


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