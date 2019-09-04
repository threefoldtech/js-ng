from jumpscale.clients.base import Client
from jumpscale.core.base import fields
import json
import types
from jumpscale.god import j


"""
name 'gedis' is not defined
JS-NG> gedis = j.clients.gedis.get("local")                                                                                   
JS-NG> gedis.list_actors()                                                                                                    
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/ahmed/wspace/js-next/js-ng/jumpscale/clients/gedis/gedis.py", line 98, in list_actors
    return json.loads(self.execute('system', 'list_actors'))
           │          └ GedisClient(__hostname='localhost', __name='local', __port=16000, _redisclient=RedisClient(_RedisClien
t__client=Redis<Connection...
           └ <module 'json' from '/usr/lib/python3.6/json/__init__.py'>
  File "/home/ahmed/wspace/js-next/js-ng/jumpscale/clients/gedis/gedis.py", line 88, in execute
    return self._redisclient.execute_command(actor_name, *args)
           │                                 │            └ ('list_actors',)
           │                                 └ 'system'
           └ GedisClient(__hostname='localhost', __name='local', __port=16000, _redisclient=RedisClient(_RedisClient__client=Redis<Connection...
  File "/home/ahmed/.cache/pypoetry/virtualenvs/js-ng-py3.6/lib/python3.6/site-packages/redis/client.py", line 839, in execute_command
    return self.parse_response(conn, command_name, **options)
           │                   │     │               └ {}
           │                   │     └ 'system'
           │                   └ Connection<host=localhost,port=6379,db=0>
           └ Redis<ConnectionPool<Connection<host=localhost,port=6379,db=0>>>
  File "/home/ahmed/.cache/pypoetry/virtualenvs/js-ng-py3.6/lib/python3.6/site-packages/redis/client.py", line 853, in parse_response
    response = connection.read_response()
               └ Connection<host=localhost,port=6379,db=0>
  File "/home/ahmed/.cache/pypoetry/virtualenvs/js-ng-py3.6/lib/python3.6/site-packages/redis/connection.py", line 717, in read_response
    raise response
          └ ResponseError("unknown command 'system'",)
redis.exceptions.ResponseError: unknown command 'system'

unknown command 'system'
JS-NG>                                                                                                                        
  …/js-ng     gedis_client    1  poetry run jsng                                         ✔  ahmed@asgard  01:06  
JS-NG> gedis = j.clients.gedis.get("local")                                                                                   
JS-NG> gedis.list_actors()                                                                                                    
['system']

JS-NG> gedis.register_actor("greeter", "/home/ahmed/wspace/js-next/js-ng/jumpscale/servers/gedis/example_greeter.py")         
1

JS-NG> gedis.list_actors()                                                                                                    
['system', 'greeter']

JS-NG>  


JS-NG> gedis.ppdoc("greeter")                                                                                                 
{
  "add2": {
    "args": [
      "a",
      "b"
    ],
    "doc": "Add two args\n        \n        "
  },
  "hi": {
    "args": [],
    "doc": "returns hello world\n        "
  },
  "info": {
    "args": [
      "result",
      "members",
      "name",
      "attr"
    ],
    "doc": ""
  },
  "ping": {
    "args": [],
    "doc": "\n        \n        "
  }
}
JS-NG> gedis.execute("greeter", "hi")                                                                                               
b'hello world'

JS-NG> gedis.execute("greeter", "ping")                                                                                             
b'pong no?'

JS-NG> gedis.execute("greeter", "add2", "first", "second")                                                                          
b'firstsecond'

JS-NG>  



 

"""

# class ActorProxy:
#     def __init__(self, actor_info):
#         ## {method: 'method_name', args: [], 'doc':...}
#         self.actor_info = actor_info

#     def __dir__(self):
#         return list(self.actor_info.keys())


#     def _method_blueprint(self, *args, **kwargs):
#         pass

    
#     def _mkmethod(self, name, args_names, docs):
#         method_blueprint_code = types.CodeType(len(args_names), 
#                             self._method_blueprint.func_code.co_nlocals,
#                             self._method_blueprint.func_code.co_stacksize,
#                             self._method_blueprint.func_code.co_flags,
#                             self._method_blueprint.func_code.co_code,
#                             self._method_blueprint.func_code.co_consts,
#                             self._method_blueprint.func_code.co_names,
#                             args_names,
#                             self._method_blueprint.func_code.co_filename,
#                             name,
#                             self._method_blueprint.func_code.co_firstlineno,
#                             self._method_blueprint.func_code.co_lnotab)


#     def __getattribute__(self, name):
#         return super().__getattribute__(name)

# class ActorsCollection:
#     def __init__(self, redis_client, actors_info):
#         self._redis_client = redis_client
#         self._actors = {}
#         self._actors_info = actors_info

#     @property
#     def actors_info(self):
#         # TODO: CHECK IF WE SHOULD USE CACHE HERE?
#         return json.loads(self._redis_client.execute_command("system", "list_actors"))

#     def __dir__(self):
#         return list(self.actors_info.keys())

#     def _load_actor(self, actor_name):
#         actor_info = json.loads(self._redis_client.execute_command(actor_name, "info"))
#         self._actors[actor_name] = ActorProxy(actor_name, actor_info)

#     def __getattr__(self, actor_name):
#         if actor_name not in self._actors:
#             self._load_actor(actor_name)


class GedisClient(Client):
    name = fields.String(default="local")
    hostname = fields.String(default="localhost")
    port = fields.Integer(default=16000)

    def __init__(self):
        super().__init__()
        self._redisclient = None
        self.redis_client

    @property
    def redis_client(self):
        if not self._redisclient:
            try:
                self._redisclient = j.clients.redis.get(f"gedis_{self.name}")
            except:
                self._redisclient = j.clients.redis.new(f"gedis_{self.name}")

        self._redisclient.hostname = self.hostname
        self._redisclient.port = self.port
        self._redisclient.save()
        return self._redisclient

    def register_actor(self, actor_name, actor_path):
        return self.execute("system", "register_actor", actor_name, actor_path)

    def execute(self, actor_name, *args):
        return self._redisclient.execute_command(actor_name, *args)

    def doc(self, actor_name):
        return json.loads(self.execute(actor_name, "info"))

    def ppdoc(self, actor_name):
        res = self.doc(actor_name)
        print(json.dumps(res, indent=2, sort_keys=True))

    def list_actors(self):
        return json.loads(self.execute("system", "list_actors"))


    