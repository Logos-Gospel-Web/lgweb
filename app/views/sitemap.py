from datetime import datetime
from django.urls import path, reverse
from django.shortcuts import redirect
from django.http import HttpRequest, HttpResponse
from .common import is_valid_language, get_base_url
from ..models import LANGUAGES, Message
from ..services.links import topic_link, message_link

def get_static_pages(base_url):
    return [[(lang, base_url + reverse(page, args=(lang,))) for lang, _ in LANGUAGES] for page in ('home', 'contact')]

def get_all_messages(base_url):
    now = datetime.now()
    msgs = Message.objects\
        .select_related('parent')\
        .filter(enabled=True, publish__lte=now, parent__enabled=True, parent__publish__lte=now)
    topics = dict()
    output = []
    for msg in msgs:
        if msg.parent.id not in topics and msg.parent.slug != 'test':
            topics[msg.parent.id] = [(lang, base_url + topic_link(msg.parent.slug, lang)) for lang, _ in LANGUAGES if msg.parent.title[lang]]
        output.append(
            [(lang, base_url + message_link(msg.parent.slug, msg.position, lang)) for lang, _ in LANGUAGES if msg.title[lang] and msg.parent.title[lang]]
        )
    return output + list(topics.values())

def get_all_pages(base_url):
    return get_static_pages(base_url) + get_all_messages(base_url)

def filter_pages_by_lang(pages, lang):
    return [[(la, url) for la, url in row if la == lang] for row in pages]

_hreflangs = {
    'tc': 'zh-TW',
    'sc': 'zh-CN',
}

def print_alternate(page):
    if len(page) > 1:
        return ''.join([f'<xhtml:link rel="alternate" hreflang="{_hreflangs[lang]}" href="{url}"></xhtml:link>' for lang, url in page])
    return ''

def print_page(page):
    alternate = print_alternate(page)
    return ''.join([f'<url><loc>{url}</loc>{alternate}</url>' for _, url in page])

def print_sitemap(pages):
    return '<?xml version="1.0" encoding="utf-8" ?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">' +\
        ''.join([print_page(page) for page in pages]) +\
        '</urlset>'

def sitemap_with_lang(request: HttpRequest, lang) -> HttpResponse:
    if not is_valid_language(lang):
        return redirect('sitemap')
    base_url = get_base_url(request)
    pages = get_all_pages(base_url)
    pages = filter_pages_by_lang(pages, lang)
    content = print_sitemap(pages)
    resp = HttpResponse(status=200, content=content, content_type='application/xml; charset=utf-8')
    return resp

def sitemap(request: HttpRequest) -> HttpResponse:
    base_url = get_base_url(request)
    pages = get_all_pages(base_url)
    content = print_sitemap(pages)
    resp = HttpResponse(status=200, content=content, content_type='application/xml; charset=utf-8')
    return resp

urlpatterns = [
    path('<slug:lang>/sitemap.xml', sitemap_with_lang, name='sitemap_lang'),
    path('sitemap.xml', sitemap, name='sitemap'),
]
