from jumpscale.core.base import StoredFactory
from .client import ZDBClientSeqMode

# userclient = StoredFactory(ZDBClient)
# adminclient = StoredFactory(ZDBAdminClient)


def get(name="test_instance", addr="localhost", port=9900, secret_="12345566", nsname="test", admin=False, mode="seq"):
    if admin == False and mode == "seq":
        return StoredFactory(ZDBClientSeqMode).get(name, addr, port, secret_, nsname, admin, mode)

