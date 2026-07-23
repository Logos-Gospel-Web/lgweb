from django.urls import path
from django.http import HttpRequest, HttpResponse

from .services.purge import purge_cache_if_needed

def purge(request: HttpRequest):
    purge_cache_if_needed()

    return HttpResponse(status=204)

urlpatterns = [
    path('purge', purge),
]
