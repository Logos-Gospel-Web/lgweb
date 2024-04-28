from django.shortcuts import render

from .common import view_func

@view_func
def error400(request, lang):
    context = request.context
    return render(request, 'site/pages/error400.html', {
        **context,
    }, status=400)

@view_func
def error404(request, lang):
    context = request.context
    return render(request, 'site/pages/error404.html', {
        **context,
    }, status=404)
