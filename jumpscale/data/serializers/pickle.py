import pickle


def dumps(obj):
    return pickle.dumps(obj)


def loads(s):
    return pickle.loads(s)
