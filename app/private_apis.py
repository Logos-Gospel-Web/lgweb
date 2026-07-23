from django.urls import path
from django.http import HttpRequest, HttpResponse

from .services.purge import purge_cache, purge_cache_if_needed

def _purge_cache(_: HttpRequest):
    purge_cache()

    return HttpResponse(status=204)

def _purge_cache_if_needed(_: HttpRequest):
    purge_cache_if_needed()

    return HttpResponse(status=204)

urlpatterns = [
    path('purge_cache', _purge_cache),
    path('purge_cache_if_needed', _purge_cache_if_needed),
]
