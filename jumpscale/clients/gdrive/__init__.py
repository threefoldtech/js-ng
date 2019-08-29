from jumpscale.core.base import StoredFactory

from .gdrive import GdriveClient


factory = StoredFactory(GdriveClient)
