from jumpscale.core.base import StoredFactory

from .peeweeClient import PeeweeClient


factory = StoredFactory(PeeweeClient)
