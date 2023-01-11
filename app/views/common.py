from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from django.utils import translation
from django.utils.translation import gettext as _
from hashlib import sha256
from os import environ

from ..services.queries import get_menu
from ..models import LANGUAGES, to_locale, Analytics

contact_email = environ.get('CONTACT_EMAIL')

_DEFAULT_LANG = 'tc'

class NotFound(Exception):
    pass

def is_valid_language(language: str) -> bool:
    return next((True for (lang, _) in LANGUAGES if lang == language), False)

def view_func(fn):
    def wrap(request, *args, **kwargs):
        if 'lang' in kwargs:
            lang = kwargs['lang']
        elif len(args) > 0:
            lang = args[0]
        else:
            return redirect('home', _DEFAULT_LANG)

        if not is_valid_language(lang):
            return redirect('home', _DEFAULT_LANG)

        translation.activate(to_locale(lang))

        try:
            context = get_base_context(request, lang)
            _save_analytics(request, context, lang)
            return fn(request, context, *args, **kwargs)
        except (ObjectDoesNotExist, NotFound):
            return redirect('home', lang)

    return wrap

def _save_analytics(request, context, lang):
    if request.method != 'GET':
        return
    headers = request.headers
    Analytics(
        ip=context['ip'],
        fingerprint=context['fingerprint'],
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

def get_base_context(request, lang):
    now = datetime.now()
    base_url = f'{request.scheme}://{request.get_host()}'
    return {
        'now': now,
        'ip': request.META['REMOTE_ADDR'],
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
