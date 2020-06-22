from jumpscale.core.base import StoredFactory
from jumpscale.servers.threebot.threebot import ThreebotServer
from jumpscale.god import j

factory = StoredFactory(ThreebotServer)
threebot = factory.get("default")
threebot.packages.add(j.packages.codeserver.__file__.rsplit("/", 1)[0])
threebot.save()
