# logging

in such a framework logging is very essential 
- stderr logs
- file rotated logs
- redis? (even allow tools like RDM to visualize logs)
- smtpd?
- notifications support (allowing to support telegram, slack, .. etc)


## loguru
[Loguru](https://github.com/Delgan/loguru) seems to be a perfect choice for our use case, easily register handlers, sane initial configurations, better datetimes, logs interceptions

### integration with notifiers

```python3
import notifiers

params = {
    "username": "you@gmail.com",
    "password": "abc123",
    "to": "dest@gmail.com"
}

# Send a single notification
notifier = notifiers.get_notifier("gmail")
notifier.notify(message="The application is running!", **params)

# Be alerted on each error message
from notifiers.logging import NotificationHandler

handler = NotificationHandler("gmail", defaults=params)
logger.add(handler, level="ERROR")
```