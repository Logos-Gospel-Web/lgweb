from urllib import request, error
import json
from os import environ

_data = {
    'to': [{ 'email': x.strip() } for x in environ.get('CONTACT_FORM_RECIPIENTS', '').split(',') if x],
    'templateId': int(environ.get('CONTACT_FORM_TEMPLATE_ID', '0')),
}

_api_key = environ.get('SENDINBLUE_API_KEY', '')

_headers = {
    'accept': 'application/json',
    'content-type': 'application/json',
    'api-key': _api_key,
}

def send_contact_email(contact_id, base_url):
    if not _api_key:
        return False

    data = json.dumps({
        **_data,
        'params': {
            'CONTACT_ID': contact_id,
            'BASE_URL': base_url,
        },
    })

    try:
        req = request.Request('https://api.sendinblue.com/v3/smtp/email', headers=_headers, data=data.encode())
        with request.urlopen(req) as resp:
            return resp.status < 300
    except (error.HTTPError, error.URLError):
        return False