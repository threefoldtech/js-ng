from jumpscale.core.base import StoredFactory
from jumpscale.servers.threebot.threebot import ThreebotServer

factory = StoredFactory(ThreebotServer)
threebot = factory.get("default")
threebot.packages.add("/sandbox/code/github/js-next/js-sdk/jumpscale/packages/codeserver/")
