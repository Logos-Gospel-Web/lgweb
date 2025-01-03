from bs4 import BeautifulSoup, PageElement, NavigableString
from django import template
from django.utils import translation
from ..models import to_lang
from django.urls import reverse

register = template.Library()

def _wrap_input(replacement: list, soup: BeautifulSoup, input: str, input_len: int, el: PageElement):
    if isinstance(el, NavigableString):
        output = []
        prev_end = 0
        lower_str = el.lower()
        index = lower_str.find(input)
        while index != -1:
            end = index + input_len
            if index > prev_end:
                output.append(el[prev_end:index])
            tag = soup.new_tag('span', attrs={ 'class': 'search__match' })
            tag.string = el[index:end]
            output.append(tag)
            prev_end = end
            index = lower_str.find(input, end)
        if len(el) > prev_end:
            output.append(el[prev_end:])
        replacement.append((el, output))
    else:
        for child in el.contents:
            _wrap_input(replacement, soup, input, input_len, child)

def wrap_input(soup: BeautifulSoup, input: str, el: PageElement):
    replacement = []
    _wrap_input(replacement, soup, input.lower(), len(input), el)

    for el, output in replacement:
        el.replace_with(*output)

@register.filter
def search_title(page, input):
    lang = to_lang(translation.get_language())
    title = getattr(page, f'title_{lang}')
    soup = BeautifulSoup(f'<h2 class="search__title">{title}</h2>')
    el = soup.h2
    wrap_input(soup, input, el)
    return el

@register.filter
def search_result(page, input):
    lang = to_lang(translation.get_language())
    content = getattr(page, f'content_{lang}')
    soup = BeautifulSoup(content, 'lxml')
    for div in soup.find_all('div', class_='box'):
        div.decompose()
    for a in soup.find_all('a'):
        del a.attrs['href']
        del a.attrs['rel']
        del a.attrs['target']
        a.name = 'span'
    root = soup.body
    selected = None
    selected_count = 0
    selected_priority = 0
    lower_input = input.lower()
    for child in root.children:
        text = child.text
        if child.name == 'p':
            if child.find('img'):
                priority = 1
            elif child.has_attr('class') and 'remark' in child['class']:
                priority = 2
            else:
                priority = 4
        else:
            priority = 3
        count = text.lower().count(lower_input) / len(text)
        if count > 0 and (priority > selected_priority or count > selected_count):
            selected = child
            selected_count = count
            selected_priority = priority

    if not selected:
        return ''

    wrap_input(soup, input, selected)

    return selected

@register.filter
def pagination_url(page, input):
    lang = to_lang(translation.get_language())
    return reverse('search', args=(lang, input, page))
