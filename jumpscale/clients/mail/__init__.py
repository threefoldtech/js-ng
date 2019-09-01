from jumpscale.core.base import StoredFactory

from .mail import MailClient


export_module_as = StoredFactory(MailClient)
