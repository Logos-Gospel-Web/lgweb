from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from datetime import date, datetime
from django.conf import settings
from django.core.cache import cache as default_cache, caches
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotModified
from django.urls import reverse
from django.utils import translation
from django.utils.timezone import get_current_timezone
from django.utils.translation import gettext as _
from django.utils.translation.trans_real import parse_accept_lang_header
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from functools import wraps
from ipware import get_client_ip
from hashlib import sha256
from os import environ
import ulid

from ..services.random_string import random_string
from ..services.queries import get_menu
from ..lang import LANGUAGES, to_locale, to_lang_tag

contact_email = environ.get('CONTACT_EMAIL')
force_https = environ.get('FORCE_HTTPS')
_head_inject = environ.get('HEAD_INJECT', '')

_PREVIEW_KEY = 'preview'
_DEFAULT_LANG = 'sc'
_BUILD_VERSION = 'dev' if settings.DEBUG else ulid.new().str
_MENU_CACHE_KEY = '__MENU__'

class NotFound(Exception):
    pass

def _get_menu_cached(now: datetime):
    value = default_cache.get(_MENU_CACHE_KEY)
    if value:
        return value
    value = get_menu(now)
    default_cache.set(_MENU_CACHE_KEY, value)
    return value

def is_valid_language(language: str) -> bool:
    return language in LANGUAGES

def _parse_preferred_language(accept: str) -> str:
    for lang, _ in parse_accept_lang_header(accept):
        if lang in ('zh-hk', 'zh-mo', 'zh-tw', 'zh-hant'):
            return 'tc'
        elif lang in ('zh-cn', 'zh-my', 'zh-sg', 'zh-hans'):
            return 'sc'
    return _DEFAULT_LANG

def view_func(allow_post = False):
    def wrapper(fn):
        @csrf_exempt
        def wrap(request, *args, **kwargs):
            if request.method == 'OPTIONS':
                return HttpResponse(status=204)

            if 'lang' in kwargs:
                lang = kwargs['lang']
            else:
                lang = next((v for v in args if is_valid_language(v)), None)

            is_lang_valid = is_valid_language(lang)

            if not is_lang_valid:
                lang = _parse_preferred_language(request.META.get('HTTP_ACCEPT_LANGUAGE', ''))
                return redirect('home', lang, permanent=True)

            request.context = _get_base_context(request, lang)
            translation.activate(to_locale(lang))

            if request.method != 'GET' and (not allow_post or request.method != 'POST'):
                return HttpResponseForbidden()

            try:
                return fn(request, *args, **kwargs)
            except (ObjectDoesNotExist, NotFound):
                return render(request, 'site/pages/error404.html', request.context, status=404)

        return wrap

    return wrapper

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

def use_cache(disabled = None):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if disabled or request.method not in ('GET', 'HEAD') or _PREVIEW_KEY in request.GET:
                return view_func(request, *args, **kwargs)

            key = request.path

            current_etag = caches['etag'].get(key)
            client_etag = request.META.get('HTTP_IF_NONE_MATCH')

            response = None

            if current_etag and client_etag:
                clean_client_etag = client_etag.replace('W/', '').strip('"')
                if clean_client_etag == current_etag:
                    response = HttpResponseNotModified()

            if not response:
                cached_data = default_cache.get(key)
                if cached_data is not None:
                    cached_content, content_type = cached_data
                    response = HttpResponse(cached_content, content_type=content_type)
                else:
                    response = view_func(request, *args, **kwargs)
                    if hasattr(response, 'render') and callable(response.render):
                        response.render()

                    if response.status_code != 200:
                        return response

                    content_type = response.get('Content-Type', 'text/html; charset=utf-8')
                    default_cache.set(key, (response.content, content_type))

                if not current_etag:
                    current_etag = random_string()
                    caches['etag'].set(key, current_etag)

            response['ETag'] = f'"{current_etag}"'
            response['Cache-Control'] = 'max-age=60'

            return response

        return _wrapped_view
    return decorator

def get_base_url(request):
    return f'{request.scheme if not force_https else "https"}://{request.get_host()}'

def get_build_version():
    return _BUILD_VERSION

def _get_base_context(request, lang):
    tz = get_current_timezone()
    now = datetime.now(tz=tz)
    has_preview = _PREVIEW_KEY in request.GET
    url_suffix = ''
    if has_preview:
        preview = request.GET[_PREVIEW_KEY]
        try:
            d = date.fromisoformat(preview)
            now = datetime(d.year, d.month, d.day, tzinfo=tz)
            url_suffix = '?preview=' + preview
        except ValueError:
            pass
    # print(now)
    base_url = get_base_url(request)
    search_form_url = reverse('search_form', args=(lang,))
    return {
        'debug': settings.DEBUG,
        'now': now,
        'base_url': base_url,
        'path': request.path,
        'full_url': base_url + request.path,
        'contact_email': contact_email,
        'menu': get_menu(now) if has_preview else _get_menu_cached(now),
        'language': lang,
        'locale': to_locale(lang),
        'lang_tag': to_lang_tag(lang),
        'build_version': _BUILD_VERSION,
        'search_form_url': search_form_url,
        'search_max_length': 20,
        'head_inject': _head_inject,
        'url_suffix': url_suffix,
    }

def make_title(title: str) -> str:
    return f'{title} | {_("聖道福音網")} Logos Gospel Web'
