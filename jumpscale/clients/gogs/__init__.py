from jumpscale.core.base import StoredFactory
from .gogs import Gogs


module_export_as = StoredFactory(Gogs)
