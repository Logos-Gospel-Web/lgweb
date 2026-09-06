from django import template
from django.utils import translation
from ..lang import to_lang

register = template.Library()

@register.filter
def is_new(message, now):
    return message.is_new(now)

@register.filter
def full_title(message, lang):
    return message.full_title(lang)

def _to_url(file):
    return file.url if file and file.name else None

def _to_dl_url(file):
    return (file.url + '&dl=1' if '?' in file.url else file.url + '?dl=1') if file and file.name else None

@register.filter
def audio(message):
    return _to_url(message.audio[to_lang(translation.get_language())] or message.audio_all)

@register.filter
def audio_dl(message):
    return _to_dl_url(message.audio[to_lang(translation.get_language())] or message.audio_all)

@register.filter
def document_dl(message):
    return _to_dl_url(message.document[to_lang(translation.get_language())])

@register.filter
def preview(content: str):
    index = content.find('<hr')
    if index == -1:
        return content
    return content[:index]
