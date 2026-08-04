from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from datetime import date, datetime
from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.urls import reverse
from django.utils import translation
from django.utils.timezone import get_current_timezone
from django.utils.translation import gettext as _
from django.utils.translation.trans_real import parse_accept_lang_header
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from os import environ

from .menu import get_menu
from ..lang import Language, is_valid_language, to_locale, to_lang_tag

_contact_email = environ.get('CONTACT_EMAIL')
_force_https = environ.get('FORCE_HTTPS')
_head_inject = environ.get('HEAD_INJECT', '')

_PREVIEW_KEY = 'preview'
_DEFAULT_LANG = 'sc'

class NotFound(Exception):
    pass

class RequestContext:
    def __init__(self, request: HttpRequest, lang: Language):
        self.debug = settings.DEBUG

        tz = get_current_timezone()
        now = datetime.now(tz=tz)
        self.now = now
        # print(now)

        has_preview = _PREVIEW_KEY in request.GET
        url_suffix = ''
        if has_preview:
            preview = request.GET[_PREVIEW_KEY]
            try:
                d = date.fromisoformat(preview)
                now = datetime(d.year, d.month, d.day, tzinfo=tz)
                url_suffix = f'?{_PREVIEW_KEY}={preview}'
            except ValueError:
                pass

        base_url = get_base_url(request)
        self.base_url = base_url
        self.path = request.path
        self.full_url = base_url + request.path
        self.url_suffix = url_suffix

        self.language = lang
        self.locale = to_locale(lang)
        self.lang_tag = to_lang_tag(lang)

        self.search_form_url = reverse('search_form', args=(lang,))
        self.search_max_length = 20

        self.menu = get_menu(now, cache=not has_preview)
        self.contact_email = _contact_email
        self.head_inject = _head_inject

    def asdict(self):
        return vars(self)

def _parse_preferred_language(accept: str) -> str:
    for lang, _ in parse_accept_lang_header(accept):
        if lang in ('zh-hk', 'zh-mo', 'zh-tw', 'zh-hant'):
            return 'tc'
        elif lang in ('zh-cn', 'zh-my', 'zh-sg', 'zh-hans'):
            return 'sc'
    return _DEFAULT_LANG

def with_context(allow_post = False):
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

            context = RequestContext(request, lang)
            translation.activate(to_locale(lang))

            try:
                return view_func(request, context, *args, **kwargs)
            except (ObjectDoesNotExist, NotFound):
                return render(request, 'site/pages/error404.html', context.asdict(), status=404)

        return _wrapped_view

    return decorator

def get_base_url(request: HttpRequest):
    return f'{request.scheme if not _force_https else "https"}://{request.get_host()}'

def make_title(title: str) -> str:
    return f'{title} | {_("聖道福音網")} Logos Gospel Web'
