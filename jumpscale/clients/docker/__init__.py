def export_module_as():

    from jumpscale.core.base import StoredFactory

    from .docker import DockerClient

    return StoredFactory(DockerClient)
