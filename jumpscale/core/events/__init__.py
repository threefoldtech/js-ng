"""
This module is for event handling, where any component can listen to certain event notifications

The modules is based on https://github.com/xmonader/events.

Events can be of any type (class), there are two ways for listening to an event:

Using decorators:

```python
from jumpscale.core.base import events

class ImportantEvent:
    def __init__(self):
        self.name = "custom event"


@events.handle(ImportantEvent)
def handle_event(ev):
    print(ev.name)
```

Or using it in your classes, just inherit from `events.Handler` and implement `handle` method.

```python3
class Impl(events.Handler):
    def __init__(self):
        events.add_listeners(self, ImprotantEvent)

    def handle(self, ev):
        print(ev.name)
```


For more control, have a look at:

- `events.add_global_listener`: for adding a global listener
- `events.handle_any` and `events.handle_many`

This can be used with base classes too, you just need to define your own custom events.
For an example, see `redis.RedisClient`
"""
from collections import defaultdict
from functools import wraps


class Any:
    pass


class Handler:
    def handle(self, ev):
        pass


listeners = defaultdict(list)
listeners[Any] = []


def add_listenter(handler, *event_types):
    if not event_types:
        raise ValueError("must specify at least 1 event type/class")
    for event_type in event_types:
        if handler not in listeners[event_type]:
            listeners[event_type].append(handler)


def add_global_listener(handler):
    add_listenter(handler, Any)


def handle_many(*event_types):
    def decorator(fun):
        add_listenter(fun, *event_types)

        @wraps(fun)
        def wrapper(*args, **kwargs):
            fun(*args, **kwargs)

        return wrapper

    return decorator


def handle_any(fun):
    add_global_listener(fun)

    @wraps(fun)
    def wrapper(*args, **kwargs):
        fun(*args, **kwargs)

    return wrapper


def handle(event_type):
    def decorator(fun):
        add_listenter(fun, event_type)

        @wraps(fun)
        def wrapper(*args, **kwargs):
            fun(*args, **kwargs)

        return wrapper

    return decorator


def notify(event):
    event_type = event.__class__
    interested = listeners.get(event_type, []) + listeners[Any]

    for handler in interested:
        if isinstance(handler, Handler):
            handler.handle(event)
        else:
            handler(event)
