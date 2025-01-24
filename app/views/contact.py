from django.shortcuts import render
from django.utils.translation import gettext as _
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.views.decorators.cache import cache_page
from django_ratelimit.core import is_ratelimited
import re

from ..services.send_email import send_contact_email
from ..models import Contact
from .common import use_etag, view_func, make_title

_keys = {
    'name': '3nj99LU9Ko',
    'email': 'Q0WBqMTnIu',
    'comment': 'Lzkq2MOlID',
    'fake': 'AKtANrG3H0',
}

def sanitize_email(email: str) -> str:
    if len(email) < 6:
        return ''
    if '@' not in email:
        return ''
    email = re.sub(r'^[\s\0.]+|[\s\0.]+$', '', email)
    local, domain = email.split('@')
    if domain.endswith('-'):
        return ''
    if not re.match(r'^[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+$', domain):
        return ''
    if not re.match(r"^[a-zA-Z0-9!#$%&'*+/=?^_`{|}~.-]+$", local):
        return ''
    return f'{local}@{domain}'

def validate_contact_form(values):
    fake = values.get(_keys['fake'], '')

    if fake:
        return dict(), dict(), True

    name = values.get(_keys['name'], '')
    email = values.get(_keys['email'], '')
    comment = values.get(_keys['comment'], '')

    errors = dict()

    if not name:
        errors['name'] = _('請輸入您的姓名')
    elif not re.match(r'^[\s.,A-Za-z\u3000\u3400-\u4DBF\u4E00-\u9FFF]+$', name):
        errors['name'] = _('請使用中文或英文字母填寫姓名')

    if not email:
        errors['email'] = _('請輸入您的電郵')
    else:
        clean_email = sanitize_email(email)
        if clean_email:
            email = clean_email
        else:
            errors['email'] = _('請輸入正確電郵')

    if not comment:
        errors['comment'] = _('請輸入內容')

    return { 'name': name, 'email': email, 'comment': comment }, errors, False

class HttpResponseSeeOther(HttpResponseRedirect):
    status_code = 303

def submit_form(values, **kwargs):
    c = Contact(**values, **kwargs)
    c.save()
    return c.id

_CONTACT_KEY = 'contact_success'

@view_func
def contact(request: HttpRequest, lang) -> HttpResponse:
    context = request.context
    status = ''
    sent = False
    failed = False

    if request.method == 'POST':
        values, errors, fake = validate_contact_form(request.POST)
        failed = len(errors) > 0

        if not failed and not fake:
            if is_ratelimited(request, key='ip', group='contact', rate='5/m', method='POST', increment=True):
                status = _('發送次數超出頻次限制，請稍後再嘗試。')
                failed = True
            else:
                id = submit_form(values, ip=context['ip'], language=lang, fingerprint=context['fingerprint'])
                send_contact_email(id, context['base_url'])

        if not failed:
            resp = HttpResponseSeeOther(request.path)
            resp.set_cookie(key=_CONTACT_KEY, value='1', path=request.path, httponly=True, samesite='Strict')
            return resp
    else:
        values, errors = dict(), dict()
        success = request.COOKIES.get(_CONTACT_KEY)
        if success == '1':
            sent = True
            status = _('您的訊息已經成功發出。')

    @use_etag(f'{request.path}:{sent}')
    @cache_page(None, key_prefix=str(sent))
    def wrap(request, lang):
        resp = render(request, 'site/pages/contact.html', {
            **context,
            'title': make_title(_('聯絡我們')),
            'keys': _keys,
            'values': values,
            'errors': errors,
            'status': status,
            'sent': sent,
        })

        if sent:
            resp.delete_cookie(key=_CONTACT_KEY, path=request.path, samesite='Strict')

        if failed:
            resp.status_code = 400

        return resp

    return wrap(request, lang)
