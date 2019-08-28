from jumpscale.clients.base import Client
from jumpscale.core.base import fields
import base64
import os
import sendgrid
from sendgrid.helpers.mail import  Mail, Attachment 


class SendGridClient(Client):
    def __init__(self):
        super().__init__()
        self.apikey = fields.String()

    def build_attachment(self, filepath, typ="application/pdf"):
        """
        Returns a valid sendgrid attachment from typical attachment object.
        """
        with open(filepath, encoding="utf-8") as fp:
            data = fp.read()
        attachment=Attachment()
        attachment.set_content(base64.b64encode(data))
        attachment.set_type(typ)
        attachment.set_filename(os.path.basename(filepath))
        attachment.set_disposition("attachment")
        return attachment

        


    def send(self, sender, subject, html_content='<strong>Email</strong>', recipients=[], attachments=[]):
        recipients=list(set(recipients))
        mail=Mail(
            from_email=sender,
            to_emails=recipients,
            subject=subject,
            html_content=html_content)
        for at in attachments:
            mail.add_attachment(at)
        try:
            sg=sendgrid.SendGridAPIClient(self.apikey)
            #response=sg.send(mail)
            response = sg.client.mail.send.post(request_body=mail.get())
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(str(e))



