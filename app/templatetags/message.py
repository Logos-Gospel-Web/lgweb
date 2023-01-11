from django import template
from django.utils import translation
from ..models import to_lang

register = template.Library()

@register.filter
def is_new(message, now):
    return message.is_new(now)

@register.filter
def full_title(message, lang):
    return message.full_title(lang)

@register.filter
def file(var):
    lang = to_lang(translation.get_language())
    x = var[lang]
    return x.url if x and x.name else None
