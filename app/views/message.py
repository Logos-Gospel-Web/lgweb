from django.shortcuts import render
from django.utils.translation import gettext as _
from django.urls import reverse
from django.db.models import Prefetch
from django.http import Http404
from django.views.decorators.cache import cache_page

from .common import use_etag, view_func, make_title, NotFound
from ..services.queries import get_messages

def get_message(slug, position, lang, now):
    return get_messages(lang, now)\
        .prefetch_related(
            Prefetch(
                'parent__children',
                queryset=get_messages(lang, now, with_parent=False))
        )\
        .get(parent__slug=slug, position=position)

def get_breadcrumb(topic, menu, lang):
    breadcrumb = [{ 'title': _('首頁'), 'url': reverse('home', args=(lang,)) }]
    topic_item = { 'title': topic.title[lang], 'url': reverse('topic', args=(lang, topic.slug)) }
    for parent in menu:
        if parent.page is not None and parent.page.id == topic.id:
            break
        for child in parent.children.all():
            if child.page is not None and child.page.id == topic.id:
                breadcrumb.append({ 'title': parent.title[lang] })
                breadcrumb.append(topic_item)
                return breadcrumb

    breadcrumb.append(topic_item)
    return breadcrumb

def get_sidebar(topic):
    children = topic.children.all()
    if topic.is_blog:
        children = children[::-1]

    return {
        'topic': topic,
        'children': children,
    }

@view_func
@use_etag()
@cache_page(None)
def message(request, lang, slug, pos):
    context = request.context
    if len(pos) == 2:
        try:
            position = int(pos) - 1
        except ValueError:
            raise NotFound()
    else:
        raise NotFound()
    now = context['now']
    page = get_message(slug, position, lang, now)
    breadcrumb = get_breadcrumb(page.parent, context['menu'], lang)
    sidebar = get_sidebar(page.parent)
    banner = page.banner[lang]
    return render(request, 'site/pages/message.html', {
        **context,
        'title': make_title(page.title[lang]),
        'fonts': [banner.subfont] if banner and banner.subfont else None,
        'message': page,
        'breadcrumb': breadcrumb,
        'sidebar': sidebar,
    })
