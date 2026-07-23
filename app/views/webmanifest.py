from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from django.utils import translation
from django.utils.translation import gettext as _

from ..lang import is_valid_language, to_locale
from ..services.view_cache import use_cache

@use_cache()
def webmanifest(request: HttpRequest, lang, hash = '0') -> HttpResponse:
    if not is_valid_language(lang):
        return HttpResponseNotFound()

    translation.activate(to_locale(lang))

    return render(request, 'site/prerendered/webmanifest.json', {
        'language': lang,
        'base_title': _("聖道福音網"),
        'favicon_hash': hash,
    }, content_type='application/manifest+json')
