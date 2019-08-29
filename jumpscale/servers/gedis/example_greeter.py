class Greeter:
    def hi(self):
        return "hello world"

    def ping(self):
        return "pong no?"

    def add2(self, a, b):
    
        print("A {} B {} ".format(a, b))
        return a+b

Actor = Greeter