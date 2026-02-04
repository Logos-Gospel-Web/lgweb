from pathlib import Path
from django.urls import path
from django.utils import translation
from django.http import HttpResponse
from django.core.files.storage import default_storage
from base64 import b64encode
from hashlib import sha256

from .models import Topic, to_locale
from .services.links import message_link, topic_link
from .services.import_doc import import_doc, process_doc
from .services.author import format_author

def admin_api(fn):
    def wrap(request, *args, **kwargs):
        if not request.user.is_active or not request.user.is_staff:
            return HttpResponse(status=401)
        if request.method == 'OPTIONS':
            return HttpResponse(status=204)
        if request.method != 'POST':
            return HttpResponse(status=405)
        return fn(request, *args, **kwargs)

    return wrap

@admin_api
def upload_doc_image_api(request):
    file = request.FILES['file']
    ext = Path(file.name).suffix

    m = sha256()
    for chunk in file.chunks():
        m.update(chunk)

    final_name = 'message/image/' + m.hexdigest() + ext
    stored_name = default_storage.save(final_name, file)

    return HttpResponse(status=200, content=default_storage.url(stored_name))

@admin_api
def import_doc_api(request):
    file = request.FILES['file']
    html = import_doc(file)

    if html is None:
        return HttpResponse(status=400)

    doc = process_doc(html)

    result = doc.to_html()

    resp = HttpResponse(status=200, content=result)
    resp['x-data-title'] = b64encode(doc.title.encode('utf-8'))
    resp['x-data-author'] = b64encode(doc.author.encode('utf-8'))
    return resp

@admin_api
def copy_doc_api(request):
    data = request.POST
    language = data['language']
    content = data['content']
    author = data['author']
    title = data['title']
    position = int(data['position'])
    year = data['year']
    if 'slug' in data:
        slug = data['slug']
    else:
        topic_id = data['topic_id']
        topic = Topic.objects.get(pk=topic_id)
        slug = topic.slug
        author = format_author(author, topic.message_author_format[language])

    translation.activate(to_locale(language))

    doc = process_doc(content)
    doc.author = author
    doc.title = title

    link = message_link(slug, position, language)
    url = f'{request.scheme}://{request.get_host()}{link}'

    html = doc.to_doc(url, year)
    return HttpResponse(status=200, content=html)

@admin_api
def get_preview_link(request):
    data = request.POST
    language = 'sc'
    position = int(data['position']) if 'position' in data else None
    if 'slug' in data:
        slug = data['slug']
    else:
        topic_id = data['topic_id']
        topic = Topic.objects.get(pk=topic_id)
        slug = topic.slug

    link = topic_link(slug, language) if position is None else message_link(slug, position, language)
    url = f'{request.scheme}://{request.get_host()}{link}'

    return HttpResponse(status=200, content=url)

urlpatterns = [
    path('document/image', upload_doc_image_api),
    path('document/import', import_doc_api),
    path('document/copy', copy_doc_api),
    path('preview', get_preview_link),
]
