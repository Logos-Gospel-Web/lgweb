from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.utils.translation import gettext as _

from ..services.purge import purge_cache

def purge(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return HttpResponseForbidden()

    purge_cache()

    return HttpResponse('Purged')
