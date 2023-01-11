from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

from .views.contact import contact
from .views.message import message
from .views.topic import topic
from .views.home import home
from .views.index import index

urlpatterns = [
    path('adminapi/', include('app.adminapis'), name='adminapi'),
    path('<slug:lang>/<slug:slug>/msg-<slug:pos>', message, name='message'),
    path('<slug:lang>/contact', contact, name='contact'),
    path('<slug:lang>/<slug:slug>', topic, name='topic'),
    path('<slug:lang>', home, name='home'),
    path('', index, name='index')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)