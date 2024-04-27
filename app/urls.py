from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .views.contact import contact
from .views.message import message
from .views.topic import topic
from .views.home import home
from .views.index import index
from .views.manifest import manifest

urlpatterns = [
    path('', include('app.views.sitemap'), name='adminapi'),
    path('adminapi/', include('app.adminapis'), name='adminapi'),
    path('<slug:lang>/manifest.json', manifest, name='manifest'),
    path('<slug:lang>/<slug:slug>/msg-<slug:pos>', message, name='message'),
    path('<slug:lang>/contact', contact, name='contact'),
    path('<slug:lang>/<slug:slug>', topic, name='topic'),
    path('<slug:lang>', home, name='home'),
    path('', index, name='index')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static('/', document_root=settings.BASE_DIR / 'public')