# Executors
Executors are very essential to execute commands on local machine or remote machine

## local

let's utilize [pyinvoke](http://docs.pyinvoke.org/en/1.3/) to run commands on local machine, also there's a `prefix` feature in commands we should keep our eyes on if we plan to do builders

## remote

use paramiko to execute commands on remote machine


# Example api

```python3
JS-NG> j.core.executors.run_local("echo $WHOME", env={'WHOME':'abc'}, ech
     1 o=True)                                                           
echo $WHOME
abc
<Result cmd='echo $WHOME' exited=0>

JS-NG> j.core.executors.run_local("uname", echo=True)                    
uname
Linux
<Result cmd='uname' exited=0>

JS-NG> j.core.executors.run_local("uname", echo=False)                   
Linux
<Result cmd='uname' exited=0>

JS-NG> with j.core.executors.RemoteExecutor(host="local
     1 host",     connect_kwargs={ 
     2         "key_filename": "/home/xmonader/.ssh/id_
...    rsa", 
     3     },) as c: 
     4     c.run("hostname")                           
xmonader-ThinkPad-E580
JS-NG>  
```