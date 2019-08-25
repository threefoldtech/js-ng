from jumpscale.clients.base import StoredFactory
from .github import Github


factory = StoredFactory(Github)
