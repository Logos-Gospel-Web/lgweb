from django.shortcuts import render
from django.db.models import Prefetch
from django.views.decorators.cache import cache_page

from ..models import with_lang, Topic
from .common import use_etag, view_func, make_title
from ..services.queries import get_messages

def get_topic_by_slug(slug, lang, now, with_children=True):
    res = Topic.objects\
        .exclude(**{ with_lang('title', lang): '' })

    if with_children:
        msgs = get_messages(lang, now, with_parent=False)
        res = res.prefetch_related(Prefetch('children', queryset=msgs))

    return res.get(slug=slug, enabled=True, publish__lte=now)

@view_func
@use_etag()
@cache_page(None)
def topic(request, lang, slug):
    context = request.context
    page = get_topic_by_slug(slug, lang, context['now'])
    template = 'blog.html' if page.is_blog else 'topic.html'
    children = page.children.all()
    has_audio = next((True for x in children if x.audio[lang]), False)

    sidebar = None
    if page.is_blog:
        sidebar = {
            'topic': page,
            'children': children[::-1],
        }
    banner = page.banner[lang]
    return render(request, f'site/pages/{template}', {
        **context,
        'title': make_title(page.title[lang]),
        'fonts': [banner.subfont] if banner and banner.subfont else None,
        'topic': page,
        'has_audio': has_audio,
        'sidebar': sidebar,
    })
