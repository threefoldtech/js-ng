# Jumpscale alerting system

## Summary
- [Overview](#overview)
- [Configuration](#configuration)
- [Types](#types)
- [APIs](#apis)

## Overview

The alerting system captures all the errors which happens in the system and store it in redis. And it has APIs to create, get and delete them.

## Configuration

The configuration is very simple

``` toml
enabled = true
level = 40
```

To get the config or to update it just do the following:

```python
JS-NG> config = j.config.get("alerts")
JS-NG> config.set("enabled", False)
JS-NG> config.set("level", 50)
```

## Types

- `bug`
- `question`
- `event_system`
- `event_monitor`
- `event_operation`


## APIs

### Raise alert
```
JS_NG> j.tools.alerthandler.alert_raise(
            appname='myapp',
            message='my error message',
            category='mycategory',
            alert_type ='event_system'
        )
```

### Search for an alert

You can search for an alert by its application name, category, message, process id, start time and last time.

Here is an example :

```
JS_NG> j.tools.alerthandler.find(appname='myapp', category='my category')
```

### Get alert details

Get an alert by its id

```python
JS-NG> j.tools.alerthandler.get(alert_id=id)
```

### Count alerts

Get the total number of alerts

```python
JS-NG> j.tools.alerthandler.count()
```

### Delete alert(s)

Delete an alert by its id

```python
JS-NG> j.tools.alerthandler.delete(alert_id=id)
```

or delete all the alerts

```python
JS-NG> j.tools.alerthandler.delete_all()
```
