from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext as _

from ..lang import Language
from ..models import HomeBanner, Promotion
from ..services.messages import get_messages
from ..services.view_cache import use_cache
from ..services.view_context import RequestContext, with_context, make_title

def get_home_banners(lang):
    return HomeBanner.objects\
        .with_topic()\
        .select_related('banner')\
        .select_related('target_page')\
        .filter(language=lang)

def get_latest_messages(lang: Language, now):
    return get_messages(lang, now).order_by('-publish')[:4]

def get_promotions(lang: Language):
    return Promotion.objects\
        .with_topic()\
        .filter(language=lang)

@with_context()
@use_cache()
def home(request: HttpRequest, context: RequestContext, lang: Language) -> HttpResponse:
    banners = get_home_banners(lang)
    return render(request, 'site/pages/home.html', {
        **context.asdict(),
        'edit_url': reverse('admin:app_homepage_change', args=[lang]),
        'title': make_title(_('首頁')),
        'banners': banners,
        'fonts': set((b.banner.subfont for b in banners if b.banner.subfont and not b.banner.hide_title)),
        'latest_messages': get_latest_messages(lang, context.now),
        'promotions': get_promotions(lang),
    })
