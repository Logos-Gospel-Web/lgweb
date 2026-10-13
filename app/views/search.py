from functools import reduce
import math
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.urls import reverse

from ..lang import Language
from ..services.messages import get_messages
from ..services.meilisearch import meili_search
from ..services.view_context import RequestContext, make_title, with_context

_PAGE_SIZE = 20

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

@with_context()
def search(request: HttpRequest, context: RequestContext, lang: Language, input: str, page=1) -> HttpResponse:
    if len(input) > context.search_max_length:
        return redirect('search', lang=lang, input=input[:context.search_max_length], page=page)

    result = meili_search(lang, input, context.now, page, _PAGE_SIZE)
    message_count = result['totalHits']
    page_title = make_title(_('搜尋結果：「%(keyword)s」的%(count)d項結果') % { 'keyword': input, 'count': message_count })

    if result['totalHits'] == 0:
        return render(request, 'site/pages/search_empty.html', {
            **context.asdict(),
            'title': page_title,
            'keyword': input,
        })

    if result['totalPages'] < page:
        return redirect('search', lang=lang, input=input, page=result['totalPages'])

    ids = [hit['id'] for hit in result['hits']]
    messages = get_messages(lang, context.now).filter(id__in=ids)
    message_dict = { msg.id: msg for msg in messages }
    messages = [{ 'message': message_dict[hit['id']] } | hit['_formatted'] for hit in result['hits'] if hit['id'] in message_dict]

    end_index = page * _PAGE_SIZE
    start_index = end_index - _PAGE_SIZE
    page_count = math.ceil(message_count / _PAGE_SIZE)

    return render(request, 'site/pages/search.html', {
        **context.asdict(),
        'title': page_title,
        'keyword': input,
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
