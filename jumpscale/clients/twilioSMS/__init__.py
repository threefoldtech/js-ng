from jumpscale.core.base import StoredFactory
from .twilioSMS import TwilioSMSClient


factory = StoredFactory(TwilioSMSClient)

