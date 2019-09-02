from jumpscale.core.base import StoredFactory
from .github import GithubClient


export_module_as = StoredFactory(GithubClient)
