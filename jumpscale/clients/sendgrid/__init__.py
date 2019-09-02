from jumpscale.core.base import StoredFactory
from .sendgrid import SendGridClient


export_module_as = StoredFactory(SendGridClient)