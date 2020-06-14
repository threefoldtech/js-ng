from jumpscale.core.base import StoredFactory
from .explorer import Explorer
from jumpscale.core.config import get_config


class ExplorerFactory(StoredFactory):
    def new(self, name, url, *args, **kwargs):
        kwargs["url"] = url
        instance = super().new(name, *args, **kwargs)
        instance.url = url
        return instance

    def get(self, name, url, *args, **kwargs):
        instance = self.find(name)
        if instance:
            return instance
        return self.new(name, url, *args, **kwargs)

    def get_default(self):
        return Explorer(get_config()["explorer"]["default_url"])

    def get_by_url(self, url):
        return Explorer(url)


def export_module_as():

    return ExplorerFactory(Explorer)
