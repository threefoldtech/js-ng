import time
from jumpscale.god import j

def time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        diff = end_time - start_time
        j.logger.info("func {} with args: {}, kwargs: {} took {}".format(func.__name__, args, kwargs, diff))
        
        return result

    return wrapper

