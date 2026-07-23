from ipware import get_client_ip
from hashlib import sha256

def get_ip(request):
    return get_client_ip(request)[0] or ''

def get_fingerprint(request):
    headers = request.headers
    raw = ':'.join((
        headers.get('user-agent', ''),
        headers.get('accept', ''),
        headers.get('accept-encoding', ''),
        headers.get('accept-language', ''),
        headers.get('cache-control', ''),
        headers.get('upgrade-insecure-requests', ''),
        headers.get('dnt', ''),
        headers.get('sec-ch-ua', ''),
        headers.get('sec-ch-ua-mobile', ''),
        headers.get('sec-ch-ua-platform', ''),
    ))
    return sha256(raw.encode('utf-8')).hexdigest()
