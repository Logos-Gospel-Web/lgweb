from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .common import view_func

@view_func(skip_analytics=True)
def error400(request: HttpRequest, lang) -> HttpResponse:
    context = request.context
    return render(request, 'site/pages/error400.html', {
        **context,
    }, status=400)

@view_func(skip_analytics=True)
def error404(request: HttpRequest, lang) -> HttpResponse:
    context = request.context
    return render(request, 'site/pages/error404.html', {
        **context,
    }, status=404)
