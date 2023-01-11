from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
from collections import defaultdict
import json
import re
from datetime import datetime
import shutil
from ...models import Topic, Message, with_lang
from ...services.import_doc import import_doc, process_doc

doc_dir_name = Path('message') / 'document'
doc_dir_path = Path(settings.MEDIA_ROOT) / doc_dir_name

def read_json(path):
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)

sites = {
    'tc': 'zh-TW',
    'sc': 'zh-CN',
}

topic_dict = defaultdict(lambda: dict(type='topic'))
message_dict = defaultdict(lambda: defaultdict(lambda: dict(type='message')))
topic_id_dict = dict()
topic_slug_dict = dict()

def load_publish(str):
    return datetime.strptime(str, '%Y-%m-%d')

def parse_topic(lang, page, meta, content, upload_dir):
    topic_id_dict[page['id']] = page['slug']
    dt = topic_dict[page['slug']]
    dt['is_blog'] = page['type'] == 'blog'
    dt['slug'] = page['slug']
    dt['publish'] = load_publish(page['publish'])
    dt[with_lang('title', lang)] = page['title']
    dt[with_lang('author', lang)] = meta.get('author', '')
    dt[with_lang('end_msg', lang)] = page['title'] + ('系列完结' if lang == 'sc' else '系列完結') if meta.get('ended') == 'on' else ''
    dt[with_lang('description', lang)] = re.sub(r'<[^>]*>', '', content)

def parse_message(lang, page, meta, content, upload_dir):
    parent_slug = topic_id_dict[page['parent']]
    dt = message_dict[parent_slug][page['slug']]
    dt['publish'] = load_publish(page['publish'])
    dt[with_lang('title', lang)] = page['title']
    dt[with_lang('author', lang)] = meta.get('author', '')
    dt['position'] = page['order'] - 1
    dt['parent_slug'] = parent_slug
    dt[with_lang('prefix', lang)] = page['prefix']
    doc_name = page.get('doc')
    if not doc_name:
        return
    doc_file = upload_dir / doc_name
    html = import_doc(str(doc_file))
    doc = process_doc(html)
    dt[with_lang('content', lang)] = doc.to_html()
    doc_dir_path.mkdir(parents=True, exist_ok=True)
    shutil.copy(doc_file, doc_dir_path / doc_name)
    dt[with_lang('document', lang)] = str(doc_dir_name / doc_name)

page_types = {
    'toc': parse_topic,
    'blog': parse_topic,
    'msg': parse_message,
}

def run(root_dir):
    for lang, code in sites.items():
        base_dir = root_dir / 'sites' / code
        pages = read_json(base_dir / 'pages.json')['pages']
        for page in pages:
            if page['type'] not in page_types:
                continue
            page_dir = base_dir / 'pages' / str(page['id'])
            meta = read_json(page_dir / 'meta.json')
            content = (page_dir / 'content.html').read_text('utf-8')
            upload_dir = page_dir / 'uploads'
            page_types[page['type']](lang, page, meta, content, upload_dir)

    for topic in topic_dict.values():
        t = Topic(**topic)
        t.save()
        topic_slug_dict[t.slug] = t

    for dts in message_dict.values():
        for msg in dts.values():
            parent_slug = msg['parent_slug']
            del msg['parent_slug']
            m = Message(**msg, parent=topic_slug_dict[parent_slug])
            m.save()

class Command(BaseCommand):
    help = 'upgrade old data.'

    def add_arguments(self, parser):
        parser.add_argument("root", type=str)

    def handle(self, *args, **options):
        self.stdout.write('Migrating old data...')
        run(Path(options['root']))
        self.stdout.write('Done.')
