from jumpscale.core.base import StoredFactory
from .client import SonicClient

export_module_as = StoredFactory(SonicClient)
