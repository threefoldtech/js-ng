from jumpscale.core.base import StoredFactory
from .client import SonicClient

factory = StoredFactory(SonicClient)
