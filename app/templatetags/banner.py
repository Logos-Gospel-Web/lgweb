from django import template
from pathlib import Path

register = template.Library()

@register.filter
def banner_text_style(banner):
    style = ''
    style += f'font-weight:{banner.font_weight};'
    style += f'color:{banner.font_color};'
    style += f'text-shadow:{banner.shadow_x / 100}em {banner.shadow_y / 100}em {banner.shadow_blur / 100}em {banner.shadow_color};'
    style += f'padding:0.2em {max(50 - banner.letter_spacing, 0) / 100}em 0.2em {max(banner.letter_spacing, 50) / 100}em;'
    style += f'letter-spacing:{banner.letter_spacing / 100}em;'
    if banner.subfont:
        style += f'font-family:{font_name(banner.subfont)};'
    return style

@register.filter
def absolute(num):
    return abs(num)

@register.filter
def font_face(font):
    return f'@font-face{{font-family:"{font_name(font)}";src:url("{font.url}")}}'

@register.filter
def srcset(banner):
    srcset = []
    if banner.image_480:
        srcset.append({ 'media': '(max-width: 480px)', 'srcset': banner.image_480.url })
    if banner.image_720:
        srcset.append({ 'media': '(max-width: 720px)', 'srcset': banner.image_720.url })
    return srcset

def font_name(font):
    return 'f' + Path(font.name).stem
