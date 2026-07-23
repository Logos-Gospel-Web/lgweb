from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
from django.shortcuts import render

from .common import is_valid_language, use_cache

@use_cache()
def favicon(request: HttpRequest, lang, hash = None) -> HttpResponse:
    if not is_valid_language(lang):
        return HttpResponseNotFound()

    return render(request, 'site/prerendered/favicons/rounded', {
        'text_template': f'./{lang}',
    }, content_type='image/svg+xml')
