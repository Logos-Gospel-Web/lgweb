import urllib.request
from os import environ
import json
from ..lang import Language, LANGUAGES
from bs4 import BeautifulSoup
from datetime import date, datetime
from django.utils.timezone import get_current_timezone

_meili_url = environ.get('MEILI_URL', '')
_meili_key = environ.get('MEILI_MASTER_KEY', '')
_meili_key = 'Bearer ' + _meili_key if _meili_key else ''

def _send_request(method: str, url: str, body = None):
    req = urllib.request.Request(
        _meili_url + url,
        data=json.dumps(body).encode('utf-8') if body else None,
        method=method,
        headers={
            'Content-Type': 'application/json',
            'Authorization': _meili_key,
        }
    )

    try:
        with urllib.request.urlopen(req) as response:
            response_data = response.read().decode('utf-8')
            return json.loads(response_data)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        return json.loads(error_body)

def _create_index(lang: Language):
    _send_request('POST', '/indexes', {
        'uid': lang,
        'primaryKey': 'id',
    })

def _config_index(lang: Language):
    _send_request('PUT', f'/indexes/{lang}/settings/localized-attributes', [{
        'locales': ['cmn'],
        'attributePatterns': ['title', 'content'],
    }])
    _send_request('PUT', f'/indexes/{lang}/settings/filterable-attributes', [
        {
            'attributePatterns': ['enabled'],
            'features': {
                'facetSearch': False,
                'filter': {
                    'equality': True,
                    'comparison': False
                }
            }
        },
        {
            'attributePatterns': ['publish'],
            'features': {
                'facetSearch': False,
                'filter': {
                    'equality': False,
                    'comparison': True
                }
            }
        }
    ])
    _send_request('PUT', f'/indexes/{lang}/settings/searchable-attributes', ['title', 'content'])
    _send_request('PUT', f'/indexes/{lang}/settings/prefix-search', 'disabled')

def _list_indexes():
    return _send_request('GET', '/indexes')

_had_ensured_indexes_exist = False

def _ensure_indexes_exist():
    global _had_ensured_indexes_exist
    if _had_ensured_indexes_exist:
        return
    resp = _list_indexes()
    remaining = set(LANGUAGES)
    for item in resp['results']:
        remaining.remove(item['uid'])
    for lang in remaining:
        _create_index(lang)
    _had_ensured_indexes_exist = True

_had_ensured_configs = False

def _ensure_configs():
    global _had_ensured_configs
    if _had_ensured_configs:
        return

    for lang in LANGUAGES:
        _config_index(lang)

    _had_ensured_configs = True

def _ensure_indexes():
    _ensure_indexes_exist()
    _ensure_configs()

def _normalize_content(content: str) -> list[str]:
    soup = BeautifulSoup(content, 'lxml')
    output = ''
    for el in soup.find_all('p', class_=False):
        output += el.text
    return output

def _to_timestamp(date: date):
    dt = datetime.combine(date, datetime.min.time(), tzinfo=get_current_timezone())
    return int(dt.timestamp())

def _update_documents(lang: Language, documents: list):
    return _send_request('POST', f'/indexes/{lang}/documents', documents)

def _delete_documents(lang: Language, ids: list[str]):
    return _send_request('POST', f'/indexes/{lang}/documents/delete-batch', ids)

def meili_update_messages(messages: list):
    _ensure_indexes()
    for lang in LANGUAGES:
        documents = []
        for message in messages:
            documents.append({
                'id': message.id,
                'title': message.title[lang],
                'content': _normalize_content(message.content[lang]),
                'publish': _to_timestamp(message.publish),
                'enabled': message.enabled,
            })
        _update_documents(lang, documents)

def meili_delete_messages(ids: str):
    _ensure_indexes()
    for lang in LANGUAGES:
        _delete_documents(lang, ids)


def meili_search(lang: Language, keyword: str, now: datetime, page: int, pagesize: int):
    _ensure_indexes()
    timestamp = int(now.timestamp())
    result = _send_request('POST', f'/indexes/{lang}/search', {
        'q': keyword,
        'filter': ['enabled = true', f'publish <= {timestamp}'],
        'attributesToRetrieve': ['id'],
        'attributesToCrop': ['content:85'],
        'attributesToHighlight': ['title', 'content'],
        'highlightPreTag': '<span class="search__match">',
        'highlightPostTag': '</span>',
        'page': page,
        'hitsPerPage': pagesize,
    })

    return result
