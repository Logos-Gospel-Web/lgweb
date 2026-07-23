from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from ..services.view_context import inject_context

@inject_context()
def error400(request: HttpRequest, lang) -> HttpResponse:
    context = request.context
    return render(request, 'site/pages/error400.html', {
        **context,
    }, status=400)

@inject_context()
def error404(request: HttpRequest, lang) -> HttpResponse:
    context = request.context
    return render(request, 'site/pages/error404.html', {
        **context,
    }, status=404)
