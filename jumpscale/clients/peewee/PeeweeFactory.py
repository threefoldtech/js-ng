from jumpscale.clients.base import Client
from jumpscale.core.base import fields
from jumpscale.god import j
from .peeweeClient import PeeweeClient

import importlib


class PeeweeFactory:
    """
    """

    __jslocation__ = "j.clients.peewee"
    _CHILDCLASS = PeeweeClient

    def _init(self):
        self.__imports__ = "peewee"
        self.clients = {}

        from .peewee import (
            PrimaryKeyField,
            BlobField,
            Model,
            BooleanField,
            TextField,
            CharField,
            IntegerField,
            SqliteDatabase,
            FloatField,
        )

        self.PrimaryKeyField = PrimaryKeyField
        self.BlobField = BlobField
        self.Model = Model
        self.BooleanField = BooleanField
        self.TextField = TextField
        self.CharField = CharField
        self.IntegerField = IntegerField
        self.SqliteDatabase = SqliteDatabase
        self.FloatField = FloatField

    # def getClient(self, ipaddr="localhost", port=5432, login="postgres", passwd="rooter", dbname="template"):
    #     key = "%s_%s_%s_%s_%s" % (ipaddr, port, login, passwd, dbname)
    #     if key not in self.clients:
    #         self.clients[key] = PostgresClient(
    #             ipaddr, port, login, passwd, dbname)
    #     return self.clients[key]

    # def getModelDoesntWorkYet(self, ipaddr="localhost", port=5432, login="postgres", passwd="rooter", dbname="template", dbtype="postgres", schema=None, cache=True):
    #     key = "%s_%s_%s_%s_%s" % (ipaddr, port, login, dbname, dbtype)
    #     if key not in self._cacheModel:
    #         pw = Pwiz(host=ipaddr, port=port, user=login, passwd=passwd, dbtype=dbtype, schema=schema, dbname=dbname)
    #         self._cacheModel[key] = pw.codeModel
    #     code = self._cacheModel[key]
    #     from IPython import embed
    #     embed()
    #     raise RuntimeError("stop debug here")

    def resetCache(self):
        """Remove peewee keys and items from db
        """
        for item in j.core.db.keys("peewee.*"):
            j.core.db.delete(item)
