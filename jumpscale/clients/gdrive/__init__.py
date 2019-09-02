from jumpscale.core.base import StoredFactory

from .gdrive import GdriveClient


export_module_as = StoredFactory(GdriveClient)
