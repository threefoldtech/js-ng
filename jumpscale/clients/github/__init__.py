from jumpscale.core.base import StoredFactory
from .github import GithubClient


factory = StoredFactory(GithubClient)
