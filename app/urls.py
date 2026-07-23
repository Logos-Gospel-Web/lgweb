from django.urls import path, include

from .views.sitemap import sitemap, sitemap_with_lang
from .views.contact import contact
from .views.message import message
from .views.topic import topic
from .views.home import home
from .views.index import index
from .views.webmanifest import webmanifest
from .views.error import error400, error404
from .views.search import search, search_form
from .views.statistics import statistics
from .views.purge import purge
from .views.analytics import analytics

urlpatterns = [
    path('', index, name='index'),
    path('adminapi/', include('app.admin_apis'), name='adminapi'),
    path('private/', include('app.private_apis'), name='privateapi'),
    path('view', analytics, name='analytics'),
    path('purge', purge, name='purge'),
    path('statistics', statistics, name='statistics'),
    path('sitemap.xml', sitemap, name='sitemap'),
    path('<slug:lang>/sitemap.xml', sitemap_with_lang, name='sitemap_lang'),
    path('<slug:lang>/contact', contact, name='contact'),
    path('<slug:lang>/error/400', error400, name='error400'),
    path('<slug:lang>/error/404', error404, name='error404'),
    path('<slug:lang>/search/<str:input>/<int:page>', search, name='search'),
    path('<slug:lang>/search', search_form, name='search_form'),
    path('<slug:lang>/<str:hash>/app.webmanifest', webmanifest, name='webmanifest'),
    path('<slug:lang>/<slug:slug>/msg-<slug:pos>', message, name='message'),
    path('<slug:lang>/<slug:slug>', topic, name='topic'),
    path('<slug:lang>', home, name='home'),
]
