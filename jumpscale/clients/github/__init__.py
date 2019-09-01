from jumpscale.core.base import StoredFactory
from .github import Github


module_export_as = StoredFactory(Github)
