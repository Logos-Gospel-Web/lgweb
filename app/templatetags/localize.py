from django import template
from django.utils import translation
from ..models import to_locale, to_lang

register = template.Library()

@register.simple_tag(takes_context=True)
def localize(context, variable):
    if isinstance(variable, str):
        return translation.gettext(variable)
    return variable[context['language']]

@register.filter(name="localize")
def localize_filter(variable):
    if isinstance(variable, str):
        return translation.gettext(variable)
    lang = to_lang(translation.get_language())
    return variable[lang]

@register.filter
def get_locale(lang):
    return to_locale(lang)
