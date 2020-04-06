from jumpscale.core.base import StoredFactory

from .docker import DockerClient


export_module_as = StoredFactory(DockerClient)
