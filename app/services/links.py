from django.urls import reverse
from django.utils import translation
from ..models import to_lang

def topic_link(slug, language=None):
    if language is None:
        language = to_lang(translation.get_language())
    return reverse('topic', args=(language, slug))

def message_link(slug, position, language=None):
    if language is None:
        language = to_lang(translation.get_language())
    return reverse('message', args=(language, slug, str(position + 1).zfill(2)))
