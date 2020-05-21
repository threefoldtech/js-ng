from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.god import j
from jumpscale.chatflows import GedisChatBot


class Example(GedisChatBot):
    steps = [
        'step_1'
    ]

    @actor_method
    def step_1(self) -> None:
        self.string_ask("Enter your name")


chat = Example