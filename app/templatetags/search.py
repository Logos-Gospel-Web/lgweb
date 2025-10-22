import math
from bs4 import BeautifulSoup, PageElement, NavigableString
from django import template
from django.utils import translation
from ..models import to_lang

register = template.Library()

def _wrap_input(replacement: list, soup: BeautifulSoup, keywords: list[str], el: PageElement):
    if isinstance(el, NavigableString):
        quote_ranges: list[tuple[int, int]] = []
        lower_str = el.lower()
        # Find all ranges that should be quoted
        for keyword in keywords:
            prev_end = 0
            keyword_len = len(keyword)
            index = lower_str.find(keyword)
            while index != -1:
                end = index + keyword_len
                quote_ranges.append((index, end))
                index = lower_str.find(keyword, end)
        if not quote_ranges:
            return

        # Filter all overlapping ranges
        quote_ranges.sort()
        ranges = [quote_ranges[0]]
        for start, end in quote_ranges[1:]:
            prev_start, prev_end = ranges[-1]
            if prev_end < start:
                ranges.append((start, end))
            elif prev_end < end:
                ranges[-1] = (prev_start, end)

        # Generate tags
        output = []
        prev_end = 0
        for start, end in ranges:
            if start > prev_end:
                output.append(el[prev_end:start])
            tag = soup.new_tag('span', attrs={ 'class': 'search__match' })
            tag.string = el[start:end]
            output.append(tag)
            prev_end = end
        if len(el) > prev_end:
            output.append(el[prev_end:])
        replacement.append((el, output))
    else:
        for child in el.contents:
            _wrap_input(replacement, soup, keywords, child)

def wrap_input(soup: BeautifulSoup, keywords: list[str], el: PageElement):
    replacement = []
    _wrap_input(replacement, soup, keywords, el)

    for el, output in replacement:
        el.replace_with(*output)

@register.filter
def search_title(page, keywords: list[str]):
    lang = to_lang(translation.get_language())
    title = getattr(page, f'title_{lang}')
    soup = BeautifulSoup(f'<h2 class="search__title">{title}</h2>', 'lxml')
    el = soup.h2
    wrap_input(soup, keywords, el)
    return el

@register.filter
def search_result(page, keywords: list[str]):
    lang = to_lang(translation.get_language())
    content = getattr(page, f'content_{lang}')
    soup = BeautifulSoup(content, 'lxml')
    for div in soup.find_all('div', class_='box'):
        div.decompose()
    root = soup.body
    selected = None
    selected_count = 0
    selected_priority = 0
    for child in root.children:
        text = child.text.lower()
        text_len = len(text)
        if text_len < 2:
            continue
        if child.name == 'p':
            if child.find('img'):
                priority = 1
            elif child.has_attr('class') and 'remark' in child['class']:
                priority = 2
            else:
                priority = 4
        else:
            priority = 3
        count = sum((text.count(k) for k in keywords)) / math.log10(text_len)
        if count > 0 and (priority > selected_priority or count > selected_count):
            selected = child
            selected_count = count
            selected_priority = priority

    if not selected:
        return ''

    for a in selected.find_all('a'):
        a.attrs.pop('href', None)
        a.attrs.pop('rel', None)
        a.attrs.pop('target', None)
        a.name = 'span'

    wrap_input(soup, keywords, selected)

    return selected
