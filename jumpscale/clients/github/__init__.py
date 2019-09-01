from jumpscale.core.base import StoredFactory
from .github import Github


export_module_as = StoredFactory(Github)
