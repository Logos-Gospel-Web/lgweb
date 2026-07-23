from django.core.cache import caches
from os import environ
from urllib.request import urlopen

from .debounce import debounce
from .has_new_page import check_has_new_page

_main_url = environ.get('MAIN_URL')

def _purge():
    caches['default'].clear()
    caches['etag'].clear()
    caches['components'].clear()
    # print('cache purged')

@debounce(0.5)
def purge_cache():
    if _main_url:
        # print('send purge_cache request')
        urlopen(f'http://{_main_url}/private/purge_cache').close()
    else:
        check_has_new_page()
        _purge()

@debounce(0.5)
def purge_cache_if_needed():
    if _main_url:
        # print('send purge_cache_if_needed request')
        urlopen(f'http://{_main_url}/private/purge_cache_if_needed').close()
    elif check_has_new_page():
        _purge()
