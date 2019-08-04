import re


class HostsFile:
    def __init__(self, hosts_file_path):
        self.path = hosts_file_path

    def exists(self, ip):
        """
        check for the existence of the ip in hosts file.
        Args:
            ip (str) : the ip address
        Return:
            boolen True or None
        """
        with open(self.path, "r") as file:
            file_content = file.read()
        result = re.search(f"{ip}", file_content)
        if result:
            return True
        else:
            return None

    def remove(self, ip):
        """
        remove the ip and its hostname from hosts file
        Args:
            ip (str) : the ip address
        """
        with open(self.path, "r") as file:
            lines = file.readlines()
        for line in lines:
            if line.startswith(f"{ip}"):
                lines.remove(line)
        with open(self.path, "w") as file:
            file.write("".join(lines))

    def add(self, ip, domain):
        """
        add new entry to the hosts file
        Args:
            ip (str) : the ip address
            domain (str) : the host name
        """
        with open(self.path, "a") as file:
            file.write(f"\n{ip}\t{domain}")

    def set_hostname(self, ip, domain):
        """
        update the hostname for ip
        Args:
            ip (str) : the ip address
            domain (str) : the host name           
        """
        self.remove(ip)
        self.add(ip, domain)

    def get_hostname(self, ip):
        """
        get the hostname for ip
        Args:
            ip (str) : the ip address
            domain (str) : the host name             
        """
        if self.exists(ip):
            with open(self.path, "r") as file:
                lines = file.readlines()
            for line in lines:
                if re.search(f"{ip}", line):
                    hostname = line.split("\t")[1]
            return hostname
        else:
            return "ip does not exist"
