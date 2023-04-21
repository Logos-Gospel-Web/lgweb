from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from django.core.cache import caches
from django.utils import translation
from django.utils.translation import gettext as _
from django.utils.translation.trans_real import parse_accept_lang_header
from django.views.decorators.cache import cache_control
from django.views.decorators.http import etag
from hashlib import sha256
from os import environ

from ..services.random_string import random_string
from ..services.ip import get_client_ip
from ..services.queries import get_menu
from ..models import LANGUAGES, to_locale, Analytics

contact_email = environ.get('CONTACT_EMAIL')

_DEFAULT_LANG = 'sc'

class NotFound(Exception):
    pass

def is_valid_language(language: str) -> bool:
    return next((True for (lang, _) in LANGUAGES if lang == language), False)

def parse_preferred_language(accept: str) -> str:
    for lang, _ in parse_accept_lang_header(accept):
        if lang in ('zh-hk', 'zh-mo', 'zh-tw', 'zh-hant'):
            return 'tc'
        elif lang in ('zh-cn', 'zh-my', 'zh-sg', 'zh-hans'):
            return 'sc'
    return _DEFAULT_LANG

def view_func(fn):
    @cache_control(must_revalidate=True, max_age=0)
    def wrap(request, *args, **kwargs):
        if 'lang' in kwargs:
            lang = kwargs['lang']
        elif len(args) > 0:
            lang = args[0]
        else:
            lang = None

        if not is_valid_language(lang):
            lang = parse_preferred_language(request.META.get('HTTP_ACCEPT_LANGUAGE', ''))
            return redirect('home', lang)

        translation.activate(to_locale(lang))
        request.context = _get_base_context(request, lang)
        _save_analytics(request, lang)

        try:
            return fn(request, *args, **kwargs)
        except (ObjectDoesNotExist, NotFound):
            return redirect('home', lang)

    return wrap

def _save_analytics(request, lang):
    if request.method != 'GET':
        return
    headers = request.headers
    Analytics(
        ip=request.context['ip'],
        fingerprint=request.context['fingerprint'],
        language=lang,
        url=request.path,
        user_agent=headers.get('user-agent', ''),
        referrer=headers.get('referer', ''),
    ).save()

def _get_fingerprint(request):
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

def use_etag(key = None):
    def etag_func(request, *args, **kwargs):
        return caches['etag'].get_or_set(request.path if key is None else key, random_string)
    return etag(etag_func)

def get_base_url(request):
    return f'{request.scheme}://{request.get_host()}'

def _get_base_context(request, lang):
    now = datetime.now()
    base_url = get_base_url(request)
    return {
        'now': now,
        'ip': get_client_ip(request),
        'fingerprint': _get_fingerprint(request),
        'base_url': base_url,
        'path': request.path,
        'full_url': base_url + request.path,
        'contact_email': contact_email,
        'menu': get_menu(),
        'language': lang,
        'locale': to_locale(lang),
    }

def make_title(title: str) -> str:
    return f'{title} | {_("聖道福音網")} Logos Gospel Web'
