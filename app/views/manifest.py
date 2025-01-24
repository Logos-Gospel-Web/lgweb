from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from django.utils import translation
from django.utils.translation import gettext as _
from django.views.decorators.cache import cache_page

from .common import get_build_version, is_valid_language, use_etag
from ..models import to_locale

@use_etag()
@cache_page(None)
def manifest(request: HttpRequest, lang) -> HttpResponse:
    if not is_valid_language(lang):
        return HttpResponseNotFound()

    translation.activate(to_locale(lang))

    return render(request, 'site/manifest.json', {
        'language': lang,
        'build_version': get_build_version(),
        'base_title': _("聖道福音網"),
    }, content_type='application/json; charset=utf-8')
