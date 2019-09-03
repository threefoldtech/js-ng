import inspect


class BaseActor:
    def info(self):
        result = {}
        members = inspect.getmembers(self)
        for name, attr in members:
            if inspect.ismethod(attr):
                result[name] = "method"
                result["args"] = [arg for arg in attr.__func__.__code__.co_varnames if arg != "self"]
                result["doc"] = attr.__doc__

        return result
