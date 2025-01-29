from django.urls import path, include

from .views.contact import contact
from .views.message import message
from .views.topic import topic
from .views.home import home
from .views.index import index
from .views.manifest import manifest
from .views.error import error400, error404
from .views.search import search, search_form
from .views.statistics import statistics
from .views.purge import purge

urlpatterns = [
    path('', include('app.views.sitemap'), name='sitemap'),
    path('adminapi/', include('app.adminapis'), name='adminapi'),
    path('purge', purge, name='purge'),
    path('statistics', statistics, name='statistics'),
    path('<slug:lang>/error/400', error400, name='error400'),
    path('<slug:lang>/error/404', error404, name='error404'),
    path('<slug:lang>/manifest.json', manifest, name='manifest'),
    path('<slug:lang>/search/<str:input>/<int:page>', search, name='search'),
    path('<slug:lang>/search', search_form, name='search_form'),
    path('<slug:lang>/<slug:slug>/msg-<slug:pos>', message, name='message'),
    path('<slug:lang>/contact', contact, name='contact'),
    path('<slug:lang>/<slug:slug>', topic, name='topic'),
    path('<slug:lang>', home, name='home'),
    path('', index, name='index')
]
