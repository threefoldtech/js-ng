from jumpscale.core.base import StoredFactory
from .gogs import Gogs


export_module_as = StoredFactory(Gogs)
