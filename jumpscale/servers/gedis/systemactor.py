import os
import sys
import json
import inspect
import warnings
from textwrap import dedent

from jumpscale.loader import j
from jumpscale.servers.gedis.baseactor import BaseActor, actor_method


class CoreActor(BaseActor):
    def __init__(self):
        super().__init__()
        self._server = None
        self.path = __file__

    def set_server(self, server):
        self._server = server

    @actor_method
    def list_actors(self) -> list:
        """List available actors

        Returns:
            list -- list of available actors
        """
        return list(self._server.actors.keys())


class SystemActor(BaseActor):
    def __init__(self):
        super().__init__()
        self._server = None
        self.path = __file__

    def set_server(self, server):
        self._server = server

    @actor_method
    def register_actor(self, actor_name: str, actor_path: str, force_reload: bool = False) -> bool:
        """
        Register new actor from a source file.

        Args:
            actor_name (str): actor name within gedis server.
            actor_path (str): actor path on gedis server machine.
            force_reload (bool, optional): reload the module if set. Defaults to False.

        Raises:
            j.exceptions.Validation: in case the actor is not valid

        Returns:
            bool: True if registered
        """
        warnings.warn(
            dedent(
                """Registering actors from the client side will be deprecated,
                please do it from gedis server, using register_actor or register_actor_module instead"""
            )
        )

        module = j.tools.codeloader.load_python_module(actor_path, force_reload=force_reload)
        self._server.register_actor_module(actor_name, module)
        return True

    @actor_method
    def unregister_actor(self, actor_name: str) -> bool:
        """Register actor

        Arguments:
            actor_name {str} -- actor name

        Returns:
            bool -- True if actors is unregistered
        """
        warnings.warn(
            dedent(
                """Unregistering actors from the client side will be deprecated,
                please do it from gedis server directly, using unregister_actor instead"""
            )
        )

        self._server.unregister_actor(actor_name)
        return True
