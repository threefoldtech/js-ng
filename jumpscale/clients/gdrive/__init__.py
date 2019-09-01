from jumpscale.core.base import StoredFactory

from .gdrive import GdriveClient


module_export_as = StoredFactory(GdriveClient)
