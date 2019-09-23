from jumpscale.core.base import StoredFactory

from .syncthing import SyncthingClient


export_module_as = StoredFactory(SyncthingClient)
