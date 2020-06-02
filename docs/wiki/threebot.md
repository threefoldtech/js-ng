- start redis
- start nginx `sudo nginx -c ~/sandbox/cfg/nginx/main/nginx.conf`
- `poetry run jsng`
- make sure to nginx configure ` j.sals.nginx.main.configure()`


```
s = j.servers.threebot.get("aa") 
s.packages.add("/home/xmonader/wspace/js-next/js-ng/jumpscale/packages/foo")  
s.save()
s.start()

```


```
➜  js-ng git:(development_threebot) ✗ curl -XPOST localhost:80/foo/actors/myactor/hello
"hello from foo's actor"%       

```
