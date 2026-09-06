from django.http import HttpRequest
from ipware import get_client_ip
from hashlib import sha256

def get_ip(request: HttpRequest):
    return get_client_ip(request)[0] or ''
