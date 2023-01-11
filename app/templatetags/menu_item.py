from django import template

register = template.Library()

@register.filter
def menu_sublist_height(children):
    return str(len(children) * 48) + 'px'
