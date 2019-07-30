import re

hosts_file = "hosts.txt"


def exists(ip, hosts_file):
    file = open(hosts_file, "r")
    file_content = file.read()
    file.close()
    return re.search(f"{ip}", file_content)


def remove(ip, hosts_file="/etc/hosts"):
    file = open(hosts_file, "r")
    lines = file.readlines()
    for line in lines:
        if line.startswith(f"{ip}"):
            lines.remove(line)
    file.close()
    file = open(hosts_file, "w")
    file.write("".join(lines))
    file.close


def add(ip, domain, hosts_file):
    file = open(hosts_file, "a")
    file.write(f"\n{ip}\t{domain}")
    file.close()


def set_hostname(ip, domain, hosts_file):
    remove(ip, hosts_file)
    add(ip, domain, hosts_file)


def get_hostname(ip, hosts_file):
    if exists(ip, hosts_file):
        file = open(hosts_file, "r")
        lines = file.readlines()
        for line in lines:
            if re.search(f"{ip}", line):
                hostname = line.split("\t")[1]
        return hostname
    else:
        return "ip does not exist"


print(get_hostname("159.0.0.0", hosts_file))

