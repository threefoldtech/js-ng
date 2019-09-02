from jumpscale.core.base import StoredFactory
from .twilio import TwilioSMSClient


export_module_as = StoredFactory(TwilioSMSClient)

