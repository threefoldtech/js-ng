from jumpscale.core.base import StoredFactory

from .git import GitClient


export_module_as = StoredFactory(GitClient)
