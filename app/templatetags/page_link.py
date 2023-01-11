from django import template
from django.urls import reverse, resolve

from ..services.links import topic_link, message_link

register = template.Library()

@register.filter
def page_link(page, slug=None):
    if page is None:
        return None
    if page.type == 'topic':
        return topic_link(slug or page.topic.slug)
    elif page.type == 'message':
        return message_link(slug or page.message.parent.slug, page.message.position)
    return None

_SWITCH_LANGUAGE = {
    'tc': 'sc',
    'sc': 'tc',
}

@register.filter
def switch_language(current_url):
    resolved = resolve(current_url)
    new_url = reverse(resolved.url_name, kwargs=resolved.kwargs | { 'lang': _SWITCH_LANGUAGE[resolved.kwargs['lang']] })
    return new_url
