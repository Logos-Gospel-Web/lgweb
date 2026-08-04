from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from ..lang import Language
from ..services.view_context import RequestContext, with_context

@with_context()
def error400(request: HttpRequest, context: RequestContext, lang: Language) -> HttpResponse:
    return render(request, 'site/pages/error400.html', {
        **context.asdict(),
    }, status=400)

@with_context()
def error404(request: HttpRequest, context: RequestContext, lang: Language) -> HttpResponse:
    return render(request, 'site/pages/error404.html', {
        **context.asdict(),
    }, status=404)
