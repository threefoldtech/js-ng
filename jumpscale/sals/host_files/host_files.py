import re


def exists(ip, hosts_file="/etc/hosts"):
    """check for the existence of the ip in hosts file and return boolen"""
    with open(hosts_file, "r") as file:
        file_content = file.read()
    result = re.search(f"{ip}", file_content)
    if result:
        return True
    else:
        return None


def remove(ip, hosts_file="/etc/hosts"):
    """remove the ip and it's hostname from hosts file"""
    with open(hosts_file, "r") as file:
        lines = file.readlines()
    for line in lines:
        if line.startswith(f"{ip}"):
            lines.remove(line)
    with open(hosts_file, "w") as file:
        file.write("".join(lines))


def add(ip, domain, hosts_file="/etc/hosts"):
    """add new entry to the database"""
    with open(hosts_file, "a") as file:
        file.write(f"\n{ip}\t{domain}")


def set_hostname(ip, domain, hosts_file="/etc/hosts"):
    """update the hostname for ip"""
    remove(ip, hosts_file)
    add(ip, domain, hosts_file)


def get_hostname(ip, hosts_file="/etc/hosts"):
    """get the the hostname for ip"""
    if exists(ip, hosts_file):
        with open(hosts_file, "r") as file:
            lines = file.readlines()
        for line in lines:
            if re.search(f"{ip}", line):
                hostname = line.split("\t")[1]
        return hostname
    else:
        return "ip does not exist"
