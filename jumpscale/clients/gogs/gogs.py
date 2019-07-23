from jumpscale.clients.base import SecureClient

class Gogs(SecureClient):
    def __init__(self, instance_name="myinstance"):
        self.instance_name = instance_name
        super().__init__(self)
