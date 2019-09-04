from jumpscale.servers.gedis.baseactor import BaseActor


class Greeter(BaseActor):
    def hi(self):
        """returns hello world
        """
        return "hello world"

    def ping(self):
        """
        
        """
        return "pong no?"

    def add2(self, a, b):
        """Add two args
        
        """
        print("A {} B {} ".format(a, b))
        return a + b


Actor = Greeter
