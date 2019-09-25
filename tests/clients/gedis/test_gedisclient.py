from jumpscale.god import j
from tests.base_tests import BaseTests


class GedisClientTest(BaseTests):
    GEDIS_SESSSION = ''

    @classmethod
    def setUpClass(cls):
        cls.info('Start gedis server in tmux session')
        session_name = "gedis_{}".format(cls.generate_random_text())
        cls.GEDIS_SESSSION = j.core.executors.tmux.create_session(session_name)
        window = cls.GEDIS_SESSSION.windows[0]
        window.attached_pane.send_keys('echo "j.servers.gedis.new_server()" | poetry run jsng')

    @classmethod
    def tearDownClass(cls):
        cls.info('Turn of the gedis server')
        cls.GEDIS_SESSSION.kill_session()

    def setUp(self):
        self.info('Get gedis client')
        self.gedis = j.clients.gedis.get('local')

    def test001_load_system_actor_by_defualt(self):
        self.info('Check system actor has been loaded')
        self.assertIn('system', self.gedis.list_actors())

    def test002_load_generator_actor(self):
        self.info('Load the generator actor')
        actor_name = "greater"
        self.gedis.register_actor(actor_name, "/opt/js-ng/jumpscale/servers/gedis/example_greeter.py")
        self.info('Assert {} actor has been loaded'.format(actor_name))
        self.assertIn(actor_name, self.gedis.list_actors())

        self.info('Assert that all actor functions have been loaded')
        self.assertEqual(['hi', 'ping', 'info', 'add2'].sort(), self.gedis.doc(actor_name).keys().sort())

    def test003_execute_actor(self):
        self.info('Load the generator actor')
        actor_name = "greater"
        self.gedis.register_actor(actor_name, "/opt/js-ng/jumpscale/servers/gedis/example_greeter.py")

        self.info('Assert ping method returns pong')
        self.assertIn('pong', self.gedis.execute(actor_name, 'ping').decode())

    def test004_execute_actor_with_params(self):
        self.info('Load the generator actor')
        actor_name = "greater"
        self.gedis.register_actor(actor_name, "/opt/js-ng/jumpscale/servers/gedis/example_greeter.py")

        self.info('Assert I can pass params to the actor methods')
        self.assertIn('0xIslamTaha', self.gedis.execute(actor_name, 'add2', '0xIslam', 'Taha').decode())

