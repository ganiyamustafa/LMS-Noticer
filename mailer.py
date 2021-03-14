import ssl
from smtplib import SMTP, SMTPAuthenticationError
from mailing_list import MailingList
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Email():  
    smtp_server = "smtp.gmail.com"
    port = 587
    server = SMTP(host='smtp.gmail.com', port=port)
    context = ssl.create_default_context()
    is_logged = False
    email = ""
    password = ""

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def login(self):
        try:
            self.server.ehlo()
            self.server.starttls(context=self.context)
            self.server.ehlo()
            self.server.login(self.email, self.password)
            self.is_logged = True
            return True
        except SMTPAuthenticationError:
            pass

    def logout(self):
        self.server.close()
        self.is_logged = False

    def get_user(self):
        if self.is_logged:
            return self.server.user