from django.test import SimpleTestCase

from ..services.author import format_author


class FormatAuthorTests(SimpleTestCase):
    def test_no_template(self):
        self.assertEqual(format_author('Alice', ''), 'Alice')
        self.assertEqual(format_author('', ''), '')
        self.assertEqual(format_author(None, None), '')

    def test_literal_template(self):
        self.assertEqual(format_author('Alice', 'Speaker'), 'Alice')
        self.assertEqual(format_author('', 'Speaker'), 'Speaker')
        self.assertEqual(format_author(None, 'Speaker'), 'Speaker')

    def test_placeholder_template(self):
        self.assertEqual(format_author('Alice', 'Speaker: {}'), 'Speaker: Alice')
        self.assertEqual(format_author('Alice', '{}'), 'Alice')
        self.assertEqual(format_author('', 'Speaker: {}'), '')
        self.assertEqual(format_author(None, '{}'), '')

    def test_invalid_templates_fall_back_to_author(self):
        with self.assertLogs('app.services.author', level='WARNING'):
            self.assertEqual(format_author('Alice', '{name}'), 'Alice')
            self.assertEqual(format_author('Alice', '{0} {1}'), 'Alice')
            self.assertEqual(format_author('Alice', '{'), 'Alice')

    def test_invalid_template_without_author_returns_empty(self):
        with self.assertLogs('app.services.author', level='WARNING'):
            self.assertEqual(format_author('', '{name}'), '')
