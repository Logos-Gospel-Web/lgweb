from django.shortcuts import render
from django.db.models import Prefetch
from django.http import HttpRequest

from ..lang import with_lang
from ..models import Topic
from ..services.messages import get_messages
from ..services.view_cache import use_cache
from ..services.view_context import inject_context, make_title

def get_topic_by_slug(slug, lang, now, with_children=True):
    res = Topic.objects\
        .exclude(**{ with_lang('title', lang): '' })

    if with_children:
        msgs = get_messages(lang, now, with_parent=False)
        res = res.prefetch_related(Prefetch('children', queryset=msgs))

    return res.get(slug=slug, enabled=True, publish__lte=now)

@inject_context()
@use_cache()
def topic(request: HttpRequest, lang, slug):
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
        'fonts': [banner.subfont] if banner and banner.subfont and not banner.hide_title else None,
        'topic': page,
        'author_label': page.message_author_label[lang],
        'has_audio': has_audio,
        'sidebar': sidebar,
        'topic_children': children,
    })
