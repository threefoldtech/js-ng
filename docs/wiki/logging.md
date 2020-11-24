# Jumpscale logging

## Summary
- [Jumpscale logging](#jumpscale-logging)
  - [Summary](#summary)
  - [Overview](#overview)
  - [Configuration](#configuration)
  - [Logging](#logging)
  - [Handlers](#handlers)
    - [Adding simple handlers](#adding-simple-handlers)
    - [Adding Custom handlers](#adding-custom-handlers)


## Overview
Our logging system is using [Loguru](https://github.com/Delgan/loguru), It seems to be a perfect choice for our use case, easily register handlers, sane initial configurations, better datetimes and logs interceptions.

The logging system has two handlers and they are enabled by default:
- `Redis handler` : Uses redis to store the logs
- `Filesystem handler` : Stores the logs in the filesystem

Both handlers can be configured or disabled by changing the logging configuration, See [configuration](#configuration) section


## Configuration
```toml
[logging]

[logging.redis]
enabled = true                  # Set this to true to enable redis handler
level = 15                      # The min severity level from which logged messages should be sent to the handler
max_size = 1000                 # Max number of logs to be kept in redis
dump = true                     # If true redis will dump the logs when it exceed the max size to file in dump_dir
dump_dir = "/tmp/logs/redis"    # Directory where the dumped logs will be saved on it

[logging.filesystem]
enabled = true                  # Set this to true to enable filesystem handler
level = 15                      # The min severity level from which logged messages should be sent to the handler
log_dir = "/tmp/fs/log.txt"     # The path of the log file
rotation = "5 MB"               # Max size of the log file, after reaching it a new file will be created.
```


## Logging
Inside your application you can log any message and all the logs will be referenced to your application, so you can get or delete them later by your application name.

By default, the application name is `init`.


```python

# register logging for app name "myapp" from current module (and sub-modules too)
j.logger.register("myapp")

j.logger.debug("my debug message")       # log debug message
j.logger.info("my info message")        # log info message
j.logger.warning("my warning message")     # log warning message
j.logger.error("my error message")       # log error message
j.logger.critical("my critical message")    # log critical message
```

Also you can set the `category` of the log message, and a `data` dict which can contains any data you want to save in the log record.

```python
j.logger.info("my info message", category="my-category", data={"key1", "value1"})
```

For exception logging you can use `j.logger.exception` to log exceptions, for example:
```python
try:
    # something raises worthless exception but it should be logged
    pass
except Exception as e:
    j.logger.exception("your message", level=30, exception=e)
```

You can unregister logging for your app using:

```
j.logger.unregister()
```

From the the same module you called `j.logger.register("myapp")`. Note that logs will be under the default app name after this.

## Handlers
You can add your own handler to the logging system and choose the min severity level from which logged messages should be sent to the handler.

### Adding simple handlers
It is just a method which expect the log record to be sent to it as an argument

```python
def my_log_handler(record):
    record = j.data.serializers.json.loads(message)["record"]
    # do somthing with the log record

j.logger.add_handler(my_log_handler, level=40)
```


### Adding Custom handlers
```python
from .logging import LogHandler

class MyCustomHandler(LogHandler):
    def __init__(self):
        self.counter = 0

    def _handle(self, message):
        record = j.data.serializers.json.loads(message)["record"]
        if record["level"]["no"] > 15:
            self.counter += 1

    def reset_counter(self):
        self.counter = 0

j.logger.add_custom_handler(name="my_custom_handler", handler=MyCustomHandler(), level=40)

```

You can access your handler class using `j.logger.<handler_name>`

```python
JS-NG> j.logger.my_custom_handler.counter
2
JS-NG> j.logger.my_custom_handler.reset_counter()
JS-NG> j.logger.my_custom_handler.counter
0
```
