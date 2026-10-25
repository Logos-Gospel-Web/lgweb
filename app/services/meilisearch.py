import json
import logging
import urllib.error
import urllib.request
from datetime import date, datetime
from os import environ

from bs4 import BeautifulSoup
from django.utils.timezone import get_current_timezone

from ..lang import LANGUAGES, Language


logger = logging.getLogger(__name__)

_had_ensured_indexes_exist = False
_had_ensured_configs = False


def _base_url() -> str:
    return environ.get('MEILI_URL', '').rstrip('/')


def _timeout() -> float:
    try:
        return float(environ.get('MEILI_TIMEOUT', '5'))
    except ValueError:
        return 5.0


def _headers() -> dict[str, str]:
    headers = {'Content-Type': 'application/json'}
    key = environ.get('MEILI_MASTER_KEY', '')
    if key:
        headers['Authorization'] = 'Bearer ' + key
    return headers


def is_meili_enabled() -> bool:
    return bool(_base_url())


def _reset_ensure_flags():
    global _had_ensured_indexes_exist, _had_ensured_configs
    _had_ensured_indexes_exist = False
    _had_ensured_configs = False


def _send_request(method: str, url: str, body=None):
    base_url = _base_url()
    if not base_url:
        return None

    req = urllib.request.Request(
        base_url + url,
        data=json.dumps(body).encode('utf-8') if body is not None else None,
        method=method,
        headers=_headers(),
    )

    try:
        with urllib.request.urlopen(req, timeout=_timeout()) as response:
            response_data = response.read().decode('utf-8')
            return json.loads(response_data)
    except urllib.error.HTTPError as e:
        try:
            error_body = e.read().decode('utf-8')[:500]
        except (OSError, UnicodeDecodeError):
            error_body = ''
        logger.warning(
            'Meilisearch %s %s failed with %s: %s',
            method, url, e.code, error_body,
        )
        _reset_ensure_flags()
        return None
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
        logger.warning('Meilisearch %s %s failed: %s', method, url, e)
        _reset_ensure_flags()
        return None


def _create_index(lang: Language) -> bool:
    return _send_request('POST', '/indexes', {
        'uid': lang,
        'primaryKey': 'id',
    }) is not None


def _config_index(lang: Language) -> bool:
    responses = [
        _send_request('PUT', f'/indexes/{lang}/settings/localized-attributes', [{
            'locales': ['cmn'],
            'attributePatterns': ['title', 'content'],
        }]),
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
        ]),
        _send_request('PUT', f'/indexes/{lang}/settings/searchable-attributes', ['title', 'content']),
        _send_request('PUT', f'/indexes/{lang}/settings/prefix-search', 'disabled'),
    ]
    return all(response is not None for response in responses)


def _list_indexes():
    return _send_request('GET', '/indexes')


def _ensure_indexes_exist() -> bool:
    global _had_ensured_indexes_exist
    if not is_meili_enabled():
        return False
    if _had_ensured_indexes_exist:
        return True

    resp = _list_indexes()
    if not isinstance(resp, dict) or not isinstance(resp.get('results'), list):
        logger.warning('Meilisearch returned an invalid index list')
        return False

    existing = {
        item.get('uid')
        for item in resp['results']
        if isinstance(item, dict)
    }
    for lang in set(LANGUAGES) - existing:
        if not _create_index(lang):
            return False

    _had_ensured_indexes_exist = True
    return True


def _ensure_configs() -> bool:
    global _had_ensured_configs
    if not is_meili_enabled():
        return False
    if _had_ensured_configs:
        return True

    for lang in LANGUAGES:
        if not _config_index(lang):
            return False

    _had_ensured_configs = True
    return True


def _ensure_indexes() -> bool:
    return _ensure_indexes_exist() and _ensure_configs()


def _normalize_content(content: str | None) -> str:
    soup = BeautifulSoup(content or '', 'lxml')
    return ''.join(el.text for el in soup.find_all('p', class_=False))


def _to_timestamp(value: date | None) -> int | None:
    if value is None:
        return None
    dt = datetime.combine(value, datetime.min.time(), tzinfo=get_current_timezone())
    return int(dt.timestamp())


def _update_documents(lang: Language, documents: list) -> bool:
    return _send_request('POST', f'/indexes/{lang}/documents', documents) is not None


def _delete_documents(lang: Language, ids: list[str]) -> bool:
    return _send_request('POST', f'/indexes/{lang}/documents/delete-batch', ids) is not None


def meili_update_messages(messages):
    if not is_meili_enabled():
        return

    messages = list(messages)
    if not messages or not _ensure_indexes():
        return

    for lang in LANGUAGES:
        documents = []
        stale_ids = []
        for message in messages:
            title = message.title[lang]
            if message.publish is None or not title:
                stale_ids.append(message.id)
                continue
            documents.append({
                'id': message.id,
                'title': title,
                'content': _normalize_content(message.content[lang]),
                'publish': _to_timestamp(message.publish),
                'enabled': message.enabled,
            })

        if documents:
            _update_documents(lang, documents)
        if stale_ids:
            _delete_documents(lang, stale_ids)


def meili_delete_messages(ids):
    if not is_meili_enabled():
        return

    ids = list(ids)
    if not ids or not _ensure_indexes():
        return

    for lang in LANGUAGES:
        _delete_documents(lang, ids)


def _empty_search_result() -> dict:
    return {'hits': [], 'totalHits': 0, 'totalPages': 0}


def meili_search(lang: Language, keyword: str, now: datetime, page: int, pagesize: int):
    if not is_meili_enabled() or not _ensure_indexes():
        return _empty_search_result()

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

    if not isinstance(result, dict) or not isinstance(result.get('hits'), list):
        return _empty_search_result()

    result.setdefault('totalHits', len(result['hits']))
    result.setdefault('totalPages', 1 if result['hits'] else 0)
    return result
