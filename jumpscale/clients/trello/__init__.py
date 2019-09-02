from jumpscale.core.base import StoredFactory

from .trello import TrelloClient


export_module_as = StoredFactory(TrelloClient)