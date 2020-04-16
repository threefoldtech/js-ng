import os
import pathlib
import docker
import sys

from jumpscale.god import j
from jumpscale.shell import ptconfig

from ptpython.repl import embed

BASE_CONFIG_DIR = os.path.join(os.environ.get("HOME", "/root"), ".jsng")
HISTORY_FILENAME = os.path.join(BASE_CONFIG_DIR, "history.txt")


class Container:
    def install(
        self, name="jsng", image="threefoldtech/js-ng:latest", ports=None, volumes=None, devices=None, identity=None
    ):
        """Creates a docker container with jsng installed on it and ready to use
        
        Keyword Arguments:
            name {str} -- Name of the new docker container (default: {"jsng"})
            image {str} -- which image you want to use (should be first contains docker) (default: {"threefoldtech/js-ng:latest"})
            ports {dict} -- ports The port number, as an integer. For example, 
                - {'2222/tcp': 3333} will expose port 2222 inside the container as port 3333 on the host. (default: {None})
            volumes volumes (dict or list) –
                A dictionary to configure volumes mounted inside the container. The key is either the host path or a volume name, and the value is a dictionary with the keys:
                bind The path to mount the volume inside the container
                mode Either rw to mount the volume read/write, or ro to mount it read-only.
                example 
                {'/home/user1/': {'bind': '/mnt/vol2', 'mode': 'rw'},
                '/var/www': {'bind': '/mnt/vol1', 'mode': 'ro'}}
            devices {list} –
                Expose host devices to the container, as a list of strings in the form <path_on_host>:<path_in_container>:<cgroup_permissions>.
                For example, /dev/sda:/dev/xvda:rwm allows the container to have read-write access to the host’s /dev/sda via a node named /dev/xvda inside the container.
            identity {str} - string contains private key
        
        Raises:
            j.exceptions.NotFound: [description]
        """
        client = j.clients.docker.get("container_install")
        try:
            cotainer = client.get(name)
            raise j.exceptions.NotFound(f"docker with name: {name} already exists, try another name")
        except docker.errors.NotFound:
            pass
        container = client.run(name, image, entrypoint="/sbin/my_init", ports=ports, volumes=volumes, devices=None)
        if identity:
            cmd = f"""/bin/sh -c 'echo "{identity}" > /root/.ssh/id_rsa ; chmod 600 /root/.ssh/id_rsa' """
            container.exec_run(cmd)


container = Container()


def run():
    os.makedirs(BASE_CONFIG_DIR, exist_ok=True)
    pathlib.Path(HISTORY_FILENAME).touch()
    if len(sys.argv) == 1:
        sys.exit(embed(globals(), locals(), configure=ptconfig, history_filename=HISTORY_FILENAME))
    else:
        sys.exit(print(eval(sys.argv[1])))
