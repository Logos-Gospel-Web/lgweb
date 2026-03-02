from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.urls import resolve
from django.urls.exceptions import Resolver404
from django.views.decorators.csrf import csrf_exempt

from .common import get_ip, get_fingerprint
from ..lang import LANGUAGES
from ..models import AnalyticsTemp

def _save_analytics(request):
    if request.method != 'POST' or 'lgweb' not in request.headers:
        return False

    body = request.body.decode('utf-8')[:2048] if request.body else ''
    if ',' not in body:
        return False

    path, referrer = body.split(',', 2)
    try:
        resolved = resolve(path)
    except Resolver404:
        return False

    if 'lang' not in resolved.kwargs:
        return False

    lang = resolved.kwargs['lang']
    if lang not in LANGUAGES:
        return False

    AnalyticsTemp(
        ip=get_ip(request),
        fingerprint=get_fingerprint(request),
        language=lang,
        url=path,
        user_agent=request.headers.get('user-agent', ''),
        referrer=referrer,
    ).save()

    return True

@csrf_exempt
def analytics(request: HttpRequest) -> HttpResponse:
    if _save_analytics(request):
        return HttpResponse(status=204)
    return HttpResponseForbidden()
