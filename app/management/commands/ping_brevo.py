from urllib import request
import json
from os import environ
import smtplib
from email.message import EmailMessage

from django.core.management.base import BaseCommand

_api_key = environ.get('BREVO_API_KEY', '')
_smtp_server = 'smtp-relay.brevo.com'
_smtp_port = 587
_smtp_login = environ.get('BREVO_SMTP_LOGIN', '')
_smtp_key = environ.get('BREVO_SMTP_KEY', '')

_target_email = environ.get('BREVO_PING_TARGET', '').strip()
_sender_name = 'Contact'
_sender_email = environ.get('CONTACT_EMAIL', '')
_subject = 'Ping'
_content = 'This is a ping email.'

_api_headers = {
    'accept': 'application/json',
    'content-type': 'application/json',
    'api-key': _api_key,
}

_api_data = json.dumps({
    'sender': {
        'name': _sender_name,
        'email': _sender_email,
    },
    'to': [{ 'email': _target_email }],
    'subject': _subject,
    'textContent': _content,
}).encode()

def _send_ping_email_through_api():
    if not _api_key or not _target_email:
        return

    req = request.Request('https://api.brevo.com/v3/smtp/email', headers=_api_headers, data=_api_data)
    with request.urlopen(req) as res:
        res.read()

def _send_ping_email_through_smtp():
    if not _smtp_key or not _target_email:
        return

    msg = EmailMessage()
    msg["Subject"] = _subject
    msg["From"] = _sender_email
    msg["To"] = _target_email
    msg.set_content(_content)

    with smtplib.SMTP(_smtp_server, _smtp_port) as server:
        server.starttls()
        server.login(_smtp_login, _smtp_key)
        server.send_message(msg)

class Command(BaseCommand):
    help = "Ping Brevo to prevent key deactivation"

    def handle(self, *args, **options):
        _send_ping_email_through_api()
        _send_ping_email_through_smtp()
