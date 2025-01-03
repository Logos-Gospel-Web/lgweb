import math
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.urls import reverse

from .common import view_func
from ..services.queries import get_messages

_PAGE_SIZE = 10

def get_pagination(current: int, count: int):
    if count <= 1:
        return None
    output = []
    if current > 1:
        # has prev page
        output.append({ 'text': _('上一頁'), 'page': current - 1 })
    if count < 9:
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

@view_func
def search(request, lang, input, page=1):
    context = request.context
    field_name = f'search_{lang}'
    matched_messages = get_messages(lang, context['now'])\
        .filter(**{ f'{field_name}__icontains': input })\
        .order_by('-publish')
    message_count = matched_messages.count()
    end_index = page * _PAGE_SIZE
    start_index = end_index - _PAGE_SIZE
    if message_count == 0:
        return render(request, 'site/pages/search_empty.html', {
            **context,
            'keyword': input,
        })
    if end_index <= 0 or start_index >= message_count:
        return redirect('search', lang=lang, input=input, page=1)
    messages = sorted(matched_messages, key=lambda msg: getattr(msg, field_name).count(input), reverse=True)[start_index:end_index]
    page_count = math.ceil(message_count / _PAGE_SIZE)
    return render(request, 'site/pages/search.html', {
        **context,
        'keyword': input,
        'messages': messages,
        'total': message_count,
        'pagination': get_pagination(page, page_count),
    })

@view_func
def search_form(request, lang):
    input = request.POST.get('q', '')
    return HttpResponseSeeOther(reverse('search', args=(lang, input, 1)))
