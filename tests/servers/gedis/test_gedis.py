import gevent
from gevent import monkey, pool
monkey.patch_all()
import time
import unittest
from jumpscale.god import j
from tests.servers.gedis.test_actor import TestObject


COUNT = 1000
POOLS_COUNT = 100
TEST_ACTOR_PATH = "/sandbox/code/github/js-next/js-ng/tests/servers/gedis/test_actor.py"
MEMORY_ACTOR_PATH = "/sandbox/code/github/js-next/js-ng/tests/servers/gedis/memory_profiler.py"


class TestGedis(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        server = j.servers.gedis.get("test")
        gevent.spawn(server.start)
        time.sleep(3)

        cls.cl = j.clients.gedis.get("test")
        cls.cl.actors.system.register_actor('test', TEST_ACTOR_PATH)
        cls.cl.actors.system.register_actor('memory', MEMORY_ACTOR_PATH)
        cls.cl.reload()


    def test01(self):
        pool = gevent.pool.Pool(POOLS_COUNT)

        def register(i):
            j.logger.info('Registering actor test_{}', i)
            self.cl.actors.system.register_actor('test_%s' % i, TEST_ACTOR_PATH)

        def execute(i):
            j.logger.info('executing actor no {}', i)
            myobject = TestObject()
            myobject.atrr = i
            response = getattr(self.cl.actors, 'test_%s' % i).add_two_numbers(1, 2)
            self.assertEqual(response.result, 3)

        def unregister(i):
            j.logger.info('Unregister actor test_{}', i)
            self.cl.actors.system.unregister_actor('test_%s' % i)
        
        jobs = []
        for i in range(COUNT):
            jobs.append(pool.spawn(register, i))

        gevent.joinall(jobs)

        self.cl.reload()

        jobs = []
        for i in range(COUNT):
            jobs.append(pool.spawn(execute, i))

        gevent.joinall(jobs)

        jobs = []
        for i in range(COUNT):
            jobs.append(pool.spawn(unregister, i))

        gevent.joinall(jobs)

        self.assertEqual(self.cl.actors.memory.object_count('TestObject').result, 0)


    def test_basic(self):
        response = self.cl.actors.test.add_two_numbers(5, 15)
        self.assertEqual(response.result, 20)

        response = self.cl.actors.test.concate_two_strings('hello', 'world')
        self.assertEqual(response.result, 'helloworld')

        obj = TestObject()
        response = self.cl.actors.test.update_object(obj, {'attr_1':1, 'attr_2': 2})
        self.assertEqual(response.result.attr_1, 1)
        self.assertEqual(response.result.attr_2, 2)

        response = self.cl.actors.test.update_objects([obj, obj], [{'attr_1':1, 'attr_2': 2}, {'attr_1':3, 'attr_2': 4}])
        self.assertEqual(response.result[0].attr_1, 1)
        self.assertEqual(response.result[0].attr_2, 2)
        self.assertEqual(response.result[1].attr_1, 3)
        self.assertEqual(response.result[1].attr_2, 4)
        

