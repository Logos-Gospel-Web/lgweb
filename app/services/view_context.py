from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from datetime import date, datetime
from django.conf import settings
from django.core.cache import cache as default_cache
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.urls import reverse
from django.utils import translation
from django.utils.timezone import get_current_timezone
from django.utils.translation import gettext as _
from django.utils.translation.trans_real import parse_accept_lang_header
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from os import environ

from ..services.queries import get_menu
from ..lang import is_valid_language, to_locale, to_lang_tag

_contact_email = environ.get('CONTACT_EMAIL')
_force_https = environ.get('FORCE_HTTPS')
_head_inject = environ.get('HEAD_INJECT', '')

_PREVIEW_KEY = 'preview'
_DEFAULT_LANG = 'sc'
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

def _parse_preferred_language(accept: str) -> str:
    for lang, _ in parse_accept_lang_header(accept):
        if lang in ('zh-hk', 'zh-mo', 'zh-tw', 'zh-hant'):
            return 'tc'
        elif lang in ('zh-cn', 'zh-my', 'zh-sg', 'zh-hans'):
            return 'sc'
    return _DEFAULT_LANG

def inject_context(allow_post = False):
    def decorator(view_func):
        @csrf_exempt
        def _wrapped_view(request: HttpRequest, *args, **kwargs):
            if request.method == 'OPTIONS':
                return HttpResponse(status=204)

            if request.method != 'GET' and (not allow_post or request.method != 'POST'):
                return HttpResponseForbidden()

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

            try:
                return view_func(request, *args, **kwargs)
            except (ObjectDoesNotExist, NotFound):
                return render(request, 'site/pages/error404.html', request.context, status=404)

        return _wrapped_view

    return decorator

def get_base_url(request: HttpRequest):
    return f'{request.scheme if not _force_https else "https"}://{request.get_host()}'

def _get_base_context(request: HttpRequest, lang):
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
        'contact_email': _contact_email,
        'menu': get_menu(now) if has_preview else _get_menu_cached(now),
        'language': lang,
        'locale': to_locale(lang),
        'lang_tag': to_lang_tag(lang),
        'search_form_url': search_form_url,
        'search_max_length': 20,
        'head_inject': _head_inject,
        'url_suffix': url_suffix,
    }

def make_title(title: str) -> str:
    return f'{title} | {_("聖道福音網")} Logos Gospel Web'
