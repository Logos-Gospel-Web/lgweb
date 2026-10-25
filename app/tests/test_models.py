import os
from unittest.mock import patch

from django.test import TestCase

from ..models import Message, Topic


class MessageModelTests(TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {'MEILI_URL': ''})
        self.env.start()
        self.addCleanup(self.env.stop)

        self.purge = patch('app.models.purge_cache')
        self.purge.start()
        self.addCleanup(self.purge.stop)

    def make_topic(self, slug='topic'):
        return Topic.objects.create(type='topic', slug=slug, is_blog=False)

    def make_message(self, topic, position=0, **kwargs):
        return Message.objects.create(
            type='message', parent=topic, position=position, **kwargs,
        )

    def test_save_notifies_meilisearch(self):
        topic = self.make_topic()
        with patch('app.signals.meili_update_messages') as update:
            message = self.make_message(topic)

        update.assert_called_once_with([message])

    def test_draft_save_does_not_raise(self):
        topic = self.make_topic()
        message = self.make_message(topic, publish=None)

        self.assertIsNone(message.publish)

    def test_direct_delete_notifies_meilisearch(self):
        topic = self.make_topic()
        message = self.make_message(topic)
        message_id = message.id

        with patch('app.signals.meili_delete_messages') as delete:
            message.delete()

        delete.assert_called_once_with([message_id])

    def test_deleting_topic_notifies_for_children(self):
        topic = self.make_topic()
        message = self.make_message(topic)
        message_id = message.id

        with patch('app.signals.meili_delete_messages') as delete:
            topic.delete()

        delete.assert_any_call([message_id])

    def test_update_reindexes_fresh_data(self):
        topic = self.make_topic()
        message = self.make_message(topic, content_tc='<p>old</p>')

        with (
            patch('app.models.is_meili_enabled', return_value=True),
            patch('app.models.meili_update_messages') as update,
        ):
            Message.objects.filter(pk=message.pk).update(
                content_tc='<p>new</p>',
            )

        update.assert_called_once()
        indexed = list(update.call_args.args[0])
        self.assertEqual(indexed[0].content_tc, '<p>new</p>')

    def test_bulk_update_reindexes_fresh_data(self):
        topic = self.make_topic()
        message = self.make_message(topic, content_tc='<p>old</p>')
        message.content_tc = '<p>new</p>'

        with (
            patch('app.models.is_meili_enabled', return_value=True),
            patch('app.models.meili_update_messages') as update,
        ):
            Message.objects.bulk_update([message], ['content_tc'])

        update.assert_called_once()
        indexed = list(update.call_args.args[0])
        self.assertEqual(indexed[0].content_tc, '<p>new</p>')
