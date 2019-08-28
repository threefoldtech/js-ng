from jumpscale.core.base import StoredFactory
from .sendgrid import SendGridClient


factory = StoredFactory(SendGridClient)