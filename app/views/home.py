from django.shortcuts import render
from django.utils.translation import gettext as _

from ..models import HomeBanner, Promotion
from .common import view_func, make_title
from ..services.queries import get_messages

def get_home_banners(lang):
    return HomeBanner.objects\
        .select_related('banner')\
        .select_related('target_page')\
        .filter(language=lang)

def get_latest_messages(lang, now):
    return get_messages(lang, now).order_by('-publish')[:4]

def get_promotions(lang):
    return Promotion.objects\
        .with_page_url()\
        .filter(language=lang)

@view_func
def home(request, context, lang):
    banners = get_home_banners(lang)
    return render(request, 'site/pages/home.html', {
        **context,
        'title': make_title(_('首頁')),
        'banners': banners,
        'fonts': [b.banner.subfont for b in banners if b.banner.subfont],
        'latest_messages': get_latest_messages(lang, context['now']),
        'promotions': get_promotions(lang),
    })
