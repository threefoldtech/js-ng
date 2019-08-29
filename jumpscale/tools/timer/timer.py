import time


def timing(callback):
    def wrapper(*args, **kwargs):
        start_point = time.time()
        result = callback(*args, **kwargs)
        end_point = time.time()
        interval = end_point - start_point
        return {"result": result, "starting": start_point, "ending": end_point, "interval": interval}

    return wrapper

