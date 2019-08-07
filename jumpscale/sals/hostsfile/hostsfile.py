import re


class HostsFile:
    def __init__(self, hosts_file_path):
        self.path = hosts_file_path
        self.content = self._parse()

    def _parse(self):
        with open(self.path, "r") as file:
            content_text = file.read()
        content_lines = content_text.splitlines()
        ip_lines = []
        regex = r"""\d+\.\d+\.\d+\.\d+"""
        for line in content_lines:
            if re.search(regex, line):
                ip_lines.append(line)
        content_dict = {}
        for line in ip_lines:
            key, value = line.split("\t")[0], line.split("\t")[1]
            content_dict[key] = value
        return content_dict

    def write(self):
        """
        write the changes into the file.
        """
        content_text = ""
        for key, value in self.content.items():
            content_text += f"\n{key}\t{value}"
        with open(self.path, "w") as file:
            file.write(content_text)

    def remove(self, ip):
        """
        remove the ip and its hostname from hosts file
        Args:
            ip (str) : the ip address
        """
        del self.content[ip]

    def add(self, ip, domain):
        """
        add new entry to the hosts file
        Args:
            ip (str) : the ip address
            domain (str) : the host name
        """
        self.content[ip] = domain

    def set_hostname(self, ip, domain):
        """
        update the hostname for ip
        Args:
            ip (str) : the ip address
            domain (str) : the host name           
        """
        self.content[ip] = domain

    def exists(self, ip):
        """
        check for the existence of the ip in hosts file.
        Args:
            ip (str) : the ip address
        Return:
            boolen expression
        """
        return ip in self.content

    def get_hostname(self, ip):
        """
        get the hostname for ip
        Args:
            ip (str) : the ip address
        Returns:
            the hostname for the ip address
        """
        return self.content[ip]
