from functools import reduce
import math
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.urls import reverse

from .common import make_title, view_func
from ..services.queries import get_messages

_PAGE_SIZE = 10

def get_pagination(current: int, count: int):
    if count <= 1:
        return None
    output = []
    if current > 1:
        # has prev page
        output.append({ 'text': _('上一頁'), 'page': current - 1 })
    if count <= 9:
        # show all page options
        for i in range(1, count + 1):
            output.append({ 'text': str(i), 'page': i, 'current': i == current })
    elif current <= 5:
        # show 1 2 3 4 5 6 7 .. 20
        for i in range(1, 8):
            output.append({ 'text': str(i), 'page': i, 'current': i == current })
        output.append({ 'text': '…' })
        output.append({ 'text': str(count), 'page': count })
    else:
        output.append({ 'text': '1', 'page': 1 })
        output.append({ 'text': '…' })
        if current > count - 5:
            # show 1 .. 14 15 16 17 18 19 20
            for i in range(count - 6, count + 1):
                output.append({ 'text': str(i), 'page': i, 'current': i == current })
        else:
            # show 1 .. 8 9 10 11 12 .. 20
            for i in range(current - 2, current + 3):
                output.append({ 'text': str(i), 'page': i, 'current': i == current })
            output.append({ 'text': '…' })
            output.append({ 'text': str(count), 'page': count })
    if current < count:
        # has next page
        output.append({ 'text': _('下一頁'), 'page': current + 1 })
    return output

class HttpResponseSeeOther(HttpResponseRedirect):
    status_code = 303

@view_func()
def search(request: HttpRequest, lang: str, input: str, page=1) -> HttpResponse:
    context = request.context
    field_name = f'search_{lang}'
    keywords = set((x.lower() for x in input.split() if x))
    # Remove keywords that contains in other keywords
    keywords = [k for k in keywords if next((False for k2 in keywords if k != k2 and k in k2), True)]
    title_trans = _('搜尋結果：「%(keyword)s」的%(count)d項結果')

    if not keywords:
        page_title = make_title(title_trans % { 'keyword': input, 'count': 0 })
        return render(request, 'site/pages/search_empty.html', {
            **context,
            'title': page_title,
            'keyword': input,
        })

    message_query = reduce(lambda a, b: a & b, [Q(**{ f'{field_name}__contains': k }) for k in keywords])
    matched_messages = get_messages(lang, context['now'])\
        .filter(message_query)\
        .order_by('-publish')
    message_count = matched_messages.count()
    end_index = page * _PAGE_SIZE
    start_index = end_index - _PAGE_SIZE
    page_title = make_title(title_trans % { 'keyword': input, 'count': message_count })
    if message_count == 0:
        return render(request, 'site/pages/search_empty.html', {
            **context,
            'title': page_title,
            'keyword': input,
        })
    if end_index <= 0 or start_index >= message_count:
        return redirect('search', lang=lang, input=input, page=1)

    title_field_name = f'title_{lang}'

    def get_count(text):
        return sum((text.count(k) for k in keywords)) / len(text)

    def get_score(msg):
        # Score more for title containing input
        content = getattr(msg, field_name)
        title = getattr(msg, title_field_name)
        return get_count(title) + get_count(content)

    messages = sorted(matched_messages, key=get_score, reverse=True)[start_index:end_index]
    page_count = math.ceil(message_count / _PAGE_SIZE)
    return render(request, 'site/pages/search.html', {
        **context,
        'title': page_title,
        'keyword': input,
        'keywords': keywords,
        'messages': messages,
        'total': message_count,
        'start_index': start_index + 1,
        'end_index': min(message_count, end_index),
        'pagination': get_pagination(page, page_count),
    })

def search_form(request: HttpRequest, lang) -> HttpResponse:
    input = request.GET.get('q', '')
    if input:
        return HttpResponseSeeOther(reverse('search', args=(lang, input, 1)))
    else:
        return redirect('home', lang)
