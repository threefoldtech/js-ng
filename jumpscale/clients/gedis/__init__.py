from jumpscale.core.base import StoredFactory

from .gedis import GedisClient


export_module_as = StoredFactory(GedisClient)

