from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from django.conf import settings
from django.core.cache import caches
from django.urls import reverse
from django.utils import translation
from django.utils.translation import gettext as _
from django.utils.translation.trans_real import parse_accept_lang_header
from django.shortcuts import render
from django.views.decorators.cache import cache_control
from django.views.decorators.http import etag
from ipware import get_client_ip
from hashlib import sha256
from os import environ
import ulid

from ..services.random_string import random_string
from ..services.queries import get_menu
from ..models import LANGUAGES, to_locale, to_lang_tag, AnalyticsTemp

contact_email = environ.get('CONTACT_EMAIL')
force_https = environ.get('FORCE_HTTPS')

_PREVIEW_KEY = 'preview'
_DEFAULT_LANG = 'sc'
_BUILD_VERSION = 'dev' if settings.DEBUG else ulid.new().str

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

def view_func(skip_analytics = False):
    def wrapper(fn):
        @cache_control(max_age=60)
        def wrap(request, *args, **kwargs):
            if 'lang' in kwargs:
                lang = kwargs['lang']
            else:
                lang = next((v for v in args if is_valid_language(v)), None)

            if not is_valid_language(lang):
                lang = parse_preferred_language(request.META.get('HTTP_ACCEPT_LANGUAGE', ''))
                return redirect('home', lang)

            translation.activate(to_locale(lang))
            request.context = _get_base_context(request, lang)

            try:
                resp = fn(request, *args, **kwargs)
                if not skip_analytics and resp.status_code < 300:
                    _save_analytics(request)
                return resp
            except (ObjectDoesNotExist, NotFound):
                return render(request, 'site/pages/error404.html', request.context, status=404)

        return wrap

    return wrapper

def _save_analytics(request):
    if request.method != 'GET':
        return
    headers = request.headers
    AnalyticsTemp(
        ip=request.context['ip'],
        fingerprint=request.context['fingerprint'],
        language=request.context['language'],
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
        return None if _PREVIEW_KEY in request.GET else caches['etag'].get_or_set(request.path if key is None else key, random_string)
    return etag(etag_func)

def get_base_url(request):
    return f'{request.scheme if not force_https else "https"}://{request.get_host()}'

def get_build_version():
    return _BUILD_VERSION

def _get_base_context(request, lang):
    now = datetime.now()
    if _PREVIEW_KEY in request.GET:
        preview = request.GET[_PREVIEW_KEY]
        try:
            now = datetime.fromisoformat(preview)
        except ValueError:
            pass
    base_url = get_base_url(request)
    search_form_url = reverse('search_form', args=(lang,))
    return {
        'now': now,
        'ip': get_client_ip(request)[0] or '',
        'fingerprint': _get_fingerprint(request),
        'base_url': base_url,
        'path': request.path,
        'full_url': base_url + request.path,
        'contact_email': contact_email,
        'menu': get_menu(),
        'language': lang,
        'locale': to_locale(lang),
        'lang_tag': to_lang_tag(lang),
        'build_version': _BUILD_VERSION,
        'search_form_url': search_form_url,
        'search_max_length': 20,
    }

def make_title(title: str) -> str:
    return f'{title} | {_("聖道福音網")} Logos Gospel Web'
