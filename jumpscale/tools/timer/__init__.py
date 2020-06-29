"""Helps with timing functions and see how long they took

example
```
JS-NG> @j.tools.timer.timeit
       def fact(n):
           if n == 1:
               return 1
           else:
               return n * fact(n-1)
JS-NG> fact(1)
2020-04-09 10:41:57.175 | INFO     | jumpscale.tools.timer.timer:wrapper:11 - func fact with args: (1,), kwargs:
{} took 2.384185791015625e-06
1

JS-NG> fact(5)
2020-04-09 10:41:59.959 | INFO     | jumpscale.tools.timer.timer:wrapper:11 - func fact with args: (1,), kwargs:
{} took 1.1920928955078125e-06
2020-04-09 10:41:59.960 | INFO     | jumpscale.tools.timer.timer:wrapper:11 - func fact with args: (2,), kwargs:
{} took 0.0003504753112792969
2020-04-09 10:41:59.960 | INFO     | jumpscale.tools.timer.timer:wrapper:11 - func fact with args: (3,), kwargs:
{} took 0.0005877017974853516
2020-04-09 10:41:59.960 | INFO     | jumpscale.tools.timer.timer:wrapper:11 - func fact with args: (4,), kwargs:
{} took 0.0008087158203125
2020-04-09 10:41:59.960 | INFO     | jumpscale.tools.timer.timer:wrapper:11 - func fact with args: (5,), kwargs: {} took 0.0010216236114501953
120
```

"""
import time
from jumpscale.loader import j


def timeit(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        diff = end_time - start_time
        j.logger.info("func {} with args: {}, kwargs: {} took {}".format(func.__name__, args, kwargs, diff))
        return result

    return wrapper
