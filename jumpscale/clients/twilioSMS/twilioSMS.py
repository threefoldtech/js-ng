from jumpscale.clients.base import Client
from jumpscale.core.base import fields

# Download the helper library from https://www.twilio.com/docs/python/install
from twilio.rest import Client as TwilioRestClient


class TwilioSMSClient(Client):
    """Your Account Sid and Auth Token from twilio.com/console
        DANGER! This is insecure. See http://twil.io/secure
    """

    account_sid = fields.String()
    auth_token = fields.String()

    def __init__(self):
        super().__init__()

    def send_sms(self, body, sender, recievers=None):
        """send sms
            Your Account Sid and Auth Token from twilio.com/console
            DANGER! This is insecure. See http://twil.io/secure
        Arguments:
            body (string) : the sms text
            sender (text) : sender full number ex: +15558675310
        
        Keyword Arguments:
            recievers (list) : recievers phone numbers
        """
        if not recievers:
            recievers = []
        tclient = TwilioRestClient(self.account_sid, self.auth_token)
        for r in recievers:
            message = tclient.messages.create(body=body, from_=sender, to=r)
            print(message.sid)

