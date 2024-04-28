from django.shortcuts import render
from django.utils.translation import gettext as _
from django.views.decorators.cache import cache_page

from .common import use_etag, view_func

@view_func
@use_etag()
@cache_page(None)
def manifest(request, lang):
    context = request.context
    return render(request, 'site/manifest.json', {
        **context,
        'base_title': _("聖道福音網"),
    }, content_type='application/json; charset=utf-8')
