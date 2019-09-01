from jumpscale.core.base import StoredFactory
from .client import SonicClient

module_export_as = StoredFactory(SonicClient)
