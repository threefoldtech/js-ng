from jumpscale.core.base import StoredFactory

from .digitalocean import DigitalOcean

export_module_as = StoredFactory(DigitalOcean)
