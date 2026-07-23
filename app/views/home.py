from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext as _

from ..models import HomeBanner, Promotion
from ..services.queries import get_messages
from ..services.view_cache import use_cache
from ..services.view_context import inject_context, make_title

def get_home_banners(lang):
    return HomeBanner.objects\
        .with_topic()\
        .select_related('banner')\
        .select_related('target_page')\
        .filter(language=lang)

def get_latest_messages(lang, now):
    return get_messages(lang, now).order_by('-publish')[:4]

def get_promotions(lang):
    return Promotion.objects\
        .with_topic()\
        .filter(language=lang)

@inject_context()
@use_cache()
def home(request: HttpRequest, lang) -> HttpResponse:
    context = request.context
    banners = get_home_banners(lang)
    return render(request, 'site/pages/home.html', {
        **context,
        'title': make_title(_('首頁')),
        'banners': banners,
        'fonts': set((b.banner.subfont for b in banners if b.banner.subfont and not b.banner.hide_title)),
        'latest_messages': get_latest_messages(lang, context['now']),
        'promotions': get_promotions(lang),
    })
