import io
import os
import urllib.error
from datetime import date, datetime
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase
from django.utils.timezone import get_current_timezone

from ..services import meilisearch


def make_message(**overrides):
    values = {
        'id': 'msg1',
        'title': {'tc': 'Title', 'sc': '標題'},
        'content': {'tc': '<p>tc</p>', 'sc': '<p>sc</p>'},
        'publish': date(2026, 1, 1),
        'enabled': True,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


class MeilisearchTests(SimpleTestCase):
    def test_disabled_does_not_send_requests(self):
        with (
            patch.dict(os.environ, {'MEILI_URL': ''}),
            patch.object(meilisearch, '_send_request') as send,
        ):
            meilisearch.meili_update_messages([make_message()])
            meilisearch.meili_delete_messages(['msg1'])
            result = meilisearch.meili_search(
                'tc', 'keyword', datetime.now(tz=get_current_timezone()), 1, 20,
            )

        send.assert_not_called()
        self.assertEqual(result, {
            'hits': [], 'totalHits': 0, 'totalPages': 0,
        })

    def test_to_timestamp(self):
        self.assertIsNone(meilisearch._to_timestamp(None))
        expected = int(datetime(
            2026, 1, 1, tzinfo=get_current_timezone(),
        ).timestamp())
        self.assertEqual(meilisearch._to_timestamp(date(2026, 1, 1)), expected)

    def test_draft_deletes_stale_documents(self):
        message = make_message(publish=None)
        with (
            patch.dict(os.environ, {'MEILI_URL': 'http://meili'}),
            patch.object(meilisearch, '_ensure_indexes', return_value=True),
            patch.object(meilisearch, '_update_documents') as update,
            patch.object(meilisearch, '_delete_documents') as delete,
        ):
            meilisearch.meili_update_messages([message])

        update.assert_not_called()
        self.assertEqual(delete.call_count, 2)
        delete.assert_any_call('tc', [message.id])
        delete.assert_any_call('sc', [message.id])

    def test_empty_translation_is_deleted(self):
        message = make_message(title={'tc': 'Title', 'sc': ''})
        with (
            patch.dict(os.environ, {'MEILI_URL': 'http://meili'}),
            patch.object(meilisearch, '_ensure_indexes', return_value=True),
            patch.object(meilisearch, '_update_documents') as update,
            patch.object(meilisearch, '_delete_documents') as delete,
        ):
            meilisearch.meili_update_messages([message])

        update.assert_called_once()
        lang, documents = update.call_args.args
        self.assertEqual(lang, 'tc')
        self.assertEqual(documents[0]['title'], 'Title')
        delete.assert_called_once_with('sc', [message.id])

    def test_extra_index_is_ignored(self):
        with (
            patch.dict(os.environ, {'MEILI_URL': 'http://meili'}),
            patch.object(meilisearch, '_had_ensured_indexes_exist', False),
            patch.object(meilisearch, '_list_indexes', return_value={
                'results': [{'uid': 'tc'}, {'uid': 'sc'}, {'uid': 'other'}],
            }),
            patch.object(meilisearch, '_create_index') as create,
        ):
            self.assertTrue(meilisearch._ensure_indexes_exist())

        create.assert_not_called()

    def test_missing_index_is_created(self):
        with (
            patch.dict(os.environ, {'MEILI_URL': 'http://meili'}),
            patch.object(meilisearch, '_had_ensured_indexes_exist', False),
            patch.object(meilisearch, '_list_indexes', return_value={
                'results': [{'uid': 'tc'}],
            }),
            patch.object(meilisearch, '_create_index', return_value=True) as create,
        ):
            self.assertTrue(meilisearch._ensure_indexes_exist())

        create.assert_called_once_with('sc')

    def test_malformed_index_list(self):
        with (
            patch.dict(os.environ, {'MEILI_URL': 'http://meili'}),
            patch.object(meilisearch, '_had_ensured_indexes_exist', False),
            patch.object(meilisearch, '_list_indexes', return_value=None),
            patch.object(meilisearch, '_create_index') as create,
        ):
            self.assertFalse(meilisearch._ensure_indexes_exist())

        create.assert_not_called()

    def test_http_error_returns_none_and_resets_flags(self):
        error = urllib.error.HTTPError(
            'http://meili/test', 500, 'error', {}, io.BytesIO(b'{}'),
        )
        with (
            patch.dict(os.environ, {'MEILI_URL': 'http://meili'}),
            patch('urllib.request.urlopen', side_effect=error),
            patch.object(meilisearch, '_had_ensured_indexes_exist', True),
            patch.object(meilisearch, '_had_ensured_configs', True),
        ):
            self.assertIsNone(meilisearch._send_request('GET', '/test'))
            self.assertFalse(meilisearch._had_ensured_indexes_exist)
            self.assertFalse(meilisearch._had_ensured_configs)

    def test_network_error_returns_none(self):
        with (
            patch.dict(os.environ, {'MEILI_URL': 'http://meili'}),
            patch(
                'urllib.request.urlopen',
                side_effect=urllib.error.URLError('down'),
            ),
        ):
            self.assertIsNone(meilisearch._send_request('GET', '/test'))

    def test_search_returns_empty_on_failure(self):
        with (
            patch.dict(os.environ, {'MEILI_URL': 'http://meili'}),
            patch.object(meilisearch, '_ensure_indexes', return_value=True),
            patch.object(meilisearch, '_send_request', return_value=None),
        ):
            result = meilisearch.meili_search(
                'tc', 'keyword', datetime.now(tz=get_current_timezone()), 1, 20,
            )

        self.assertEqual(result, {'hits': [], 'totalHits': 0, 'totalPages': 0})

    def test_search_returns_empty_on_malformed_result(self):
        with (
            patch.dict(os.environ, {'MEILI_URL': 'http://meili'}),
            patch.object(meilisearch, '_ensure_indexes', return_value=True),
            patch.object(meilisearch, '_send_request', return_value={
                'message': 'index not found',
            }),
        ):
            result = meilisearch.meili_search(
                'tc', 'keyword', datetime.now(tz=get_current_timezone()), 1, 20,
            )

        self.assertEqual(result, {'hits': [], 'totalHits': 0, 'totalPages': 0})

    def test_normalize_content(self):
        content = '<p>a</p><p class="x">b</p><p>c</p>'
        self.assertEqual(meilisearch._normalize_content(content), 'ac')
        self.assertEqual(meilisearch._normalize_content(None), '')
