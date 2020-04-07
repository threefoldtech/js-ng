from jumpscale.core.base import StoredFactory
from .client import ZDBClient, ZDBAdminClient

regular = StoredFactory(ZDBClient)
admin = StoredFactory(ZDBAdminClient)
