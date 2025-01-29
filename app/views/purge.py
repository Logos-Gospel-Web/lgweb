from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.utils.translation import gettext as _
from django.core.cache import caches

def purge(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return HttpResponseForbidden()

    caches['default'].clear()
    caches['etag'].clear()

    return HttpResponse('Purged')
