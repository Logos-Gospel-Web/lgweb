import os
from datetime import date, datetime
from unittest.mock import patch

from django.test import TestCase
from django.utils.timezone import get_current_timezone

from ..models import (
    Banner, ChildMenuItem, HomeBanner, HomePage, ParentMenuItem, Promotion, Topic,
)
from ..views.home import get_home_banners, get_promotions


class PublishSchedulingTests(TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {'MEILI_URL': ''})
        self.env.start()
        self.addCleanup(self.env.stop)

        self.purge = patch('app.models.purge_cache')
        self.purge.start()
        self.addCleanup(self.purge.stop)

        self.now = datetime(2026, 6, 15, 12, 0, tzinfo=get_current_timezone())

    def make_topic(self, slug='topic'):
        return Topic.objects.create(
            type='topic', slug=slug, is_blog=False,
            publish=date(2016, 1, 1),
        )

    def make_banner(self):
        return Banner.objects.create(title='Banner', image='banner/image/banner.png')

    def make_home_banner(self, publish, position=0, language='tc'):
        return HomeBanner.objects.create(
            language=HomePage.objects.get(pk=language),
            position=position,
            publish=publish,
            banner=self.make_banner(),
        )

    def make_promotion(self, publish, position=0):
        return Promotion.objects.create(
            language=HomePage.objects.get(pk='tc'),
            position=position,
            publish=publish,
            image='promotion/image/promotion.png',
            title='Title',
            description='Description',
            page=self.make_topic(f'topic-{position}'),
        )

    def make_parent_menu(self, publish, position=0):
        return ParentMenuItem.objects.create(
            position=position, title_tc='Title', title_sc='Title', publish=publish,
        )

    def make_child_menu(self, parent, publish, position=0):
        return ChildMenuItem.objects.create(
            parent=parent, position=position, title_tc='Title', title_sc='Title',
            publish=publish, page=self.make_topic(f'topic-{publish}-{position}'),
        )

    def test_home_banner_appears_on_publish_date(self):
        visible = self.make_home_banner(date(2016, 1, 1), position=0)
        hidden = self.make_home_banner(date(2026, 12, 1), position=1)
        draft = self.make_home_banner(None, position=2)

        result = list(get_home_banners('tc', self.now))

        self.assertIn(visible, result)
        self.assertNotIn(hidden, result)
        self.assertNotIn(draft, result)

    def test_home_banner_publish_today_is_visible(self):
        banner = self.make_home_banner(date(2026, 6, 15))

        self.assertIn(banner, list(get_home_banners('tc', self.now)))

    def test_home_banner_not_visible_before_publish_date(self):
        banner = self.make_home_banner(date(2026, 6, 16))

        self.assertNotIn(banner, list(get_home_banners('tc', self.now)))

    def test_promotion_appears_on_publish_date(self):
        visible = self.make_promotion(date(2016, 1, 1), position=0)
        hidden = self.make_promotion(date(2026, 12, 1), position=1)
        draft = self.make_promotion(None, position=2)

        result = list(get_promotions('tc', self.now))

        self.assertIn(visible, result)
        self.assertNotIn(hidden, result)
        self.assertNotIn(draft, result)

    def test_parent_menu_item_appears_on_publish_date(self):
        visible = self.make_parent_menu(date(2016, 1, 1), position=0)
        hidden = self.make_parent_menu(date(2026, 12, 1), position=1)
        draft = self.make_parent_menu(None, position=2)

        result = list(ParentMenuItem.objects.filter_disabled_item(self.now, True))

        self.assertIn(visible, result)
        self.assertNotIn(hidden, result)
        self.assertNotIn(draft, result)

    def test_child_menu_item_appears_on_publish_date(self):
        parent = self.make_parent_menu(date(2016, 1, 1))
        visible = self.make_child_menu(parent, date(2016, 1, 1), position=0)
        hidden = self.make_child_menu(parent, date(2026, 12, 1), position=1)
        draft = self.make_child_menu(parent, None, position=2)

        result = list(ChildMenuItem.objects.filter_disabled_item(self.now, False))

        self.assertIn(visible, result)
        self.assertNotIn(hidden, result)
        self.assertNotIn(draft, result)
