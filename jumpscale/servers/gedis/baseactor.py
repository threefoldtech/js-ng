import inspect
import json

class BaseActor:
    def info(self):
        result = {}
        members = inspect.getmembers(self)
        for name, attr in members:
            if inspect.ismethod(attr):
                result[name] = {}
                result[name]["args"] = [arg for arg in attr.__func__.__code__.co_varnames if arg != "self"]
                result[name]["doc"] = attr.__doc__ or ""

        return json.dumps(result)
