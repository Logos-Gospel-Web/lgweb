from django.core.cache import caches
from os import environ
from urllib.request import urlopen

from .has_new_page import check_has_new_page

_main_url = environ.get('MAIN_URL')

def _purge():
    caches['default'].clear()
    caches['etag'].clear()
    caches['components'].clear()

def purge_cache():
    if _main_url:
        urlopen(f'http://{_main_url}/private/purge_cache').close()
    else:
        check_has_new_page()
        _purge()

def purge_cache_if_needed():
    if _main_url:
        urlopen(f'http://{_main_url}/private/purge_cache_if_needed').close()
    elif check_has_new_page():
        _purge()
