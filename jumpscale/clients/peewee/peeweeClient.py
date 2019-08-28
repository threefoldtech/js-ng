from jumpscale.clients.base import Client
from jumpscale.core.base import fields
import importlib
from jumpscale.god import j


class PeeweeClient(Client):

    name = fields.String()
    ipaddr = fields.String(default="localhost")
    port = fields.Integer(default=0)
    login = fields.String(default="postgres")
    passwd_ = fields.String()
    dbname = fields.String(default="template")
    dbtype = fields.String(default="postgres")
    peeweeschema = fields.String()
    cache = fields.Boolean(default=True)

    def __init__(self):
        super().__init__()
        self.passwd = fields.String()
        self._model = fields.String()
 
    @property
    def model(self):
        if self._model:
            return self._model
        key = "%s_%s_%s_%s_%s" % (self.ipaddr, self.port, self.login, self.dbname, self.dbtype)

        if j.core.db.get("peewee.code.%s" % key) is None:
            cmd = 'pwiz.py -H %s  -p %s -u "%s" -P -i %s' % (self.ipaddr, self.port, self.login, self.dbname)
            out = j.sal.process.execute(cmd, useShell=True, die=True, showout=False)
            j.core.db.set("peewee.code.%s" % key, out)
        code = j.core.db.get("peewee.code.%s" % key).decode()

        path = j.sal.fs.joinPaths(j.dirs.TMPDIR, "peewee", key + ".py")
        j.sal.fs.createDir(j.sal.fs.joinPaths(j.dirs.TMPDIR, "peewee"))
        j.sal.fs.writeFile(path, code)

        loader = importlib.machinery.SourceFileLoader(key, path)
        module = loader.load_module(key)

        self._model = module
        return module
