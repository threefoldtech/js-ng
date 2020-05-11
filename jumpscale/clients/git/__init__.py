def export_module_as():

    from jumpscale.core.base import StoredFactory

    from .git import GitClient

    return StoredFactory(GitClient)
