from jumpscale.clients.base import ClientFactory
from .github import Github

factory = ClientFactory(Github)
