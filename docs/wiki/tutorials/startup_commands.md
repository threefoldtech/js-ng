# Startup Commands
This module manages long running commands
## To start a python http server
```
JS-NG> cmd = j.tools.startupcmd.get("cmd_name")

JS-NG> cmd.start_cmd = "python3 -m http.server"

JS-NG> cmd.start()

```
## Check if it is running

```
JS-NG> cmd.is_running()
True
```
## Stopping the running command
```
JS-NG> cmd.stop()
```
## Getting pid of the running process(command)
```
JS-NG> cmd.pid()
2132
```
## Getting process of the running command
```
JS-NG> cmd.process()                                                                 
psutil.Process(pid=968692, name='python3', started='00:34:01')
```
### Waiting for a command to stop
```
cmd.wait_for_stop()
```
## Waiting for a command to start
```
cmd.wait_for_running()
```