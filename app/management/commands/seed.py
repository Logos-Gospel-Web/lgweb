from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.conf import settings
from django.core.files.base import File
from ...models import LANGUAGES, HomePage, Topic, Message, ParentMenuItem, ChildMenuItem, Promotion, Banner, HomeBanner
from ...services.random_string import random_string
import urllib.request
import datetime
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

class Command(BaseCommand):
    help = 'seed database.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')
        run_seed()
        self.stdout.write('Done.')

def run_seed():
    User = get_user_model()
    try:
        User.objects.create_superuser('admin', 'admin@example.com', 'secret')
    except IntegrityError:
        pass
    for (lang, _) in LANGUAGES:
        homepage = HomePage(language=lang)
        homepage.save()
    if settings.DEBUG:
        add_sample_data()

def add_sample_data():
    if Topic.objects.exists():
        return

    def random_image_name():
        return random_string() + '.jpeg'

    def download_random_image(width, height):
        url = f'https://picsum.photos/{width}/{height}'
        return urllib.request.urlopen(url)

    def create_topic(idx: int, banner = None, is_blog = False):
        topic = Topic(
            type = 'topic',
            enabled = True,
            publish = datetime.date(2016 + idx // 12, 1 + idx % 12, 1),
            title_tc = f'Topic {idx} TC',
            title_sc = f'Topic {idx} SC',
            author_tc = f'Author {idx} TC',
            author_sc = f'Author {idx} SC',
            banner_tc = banner,
            banner_sc = banner,
            slug = f'topic{idx}',
            is_blog = is_blog,
        )
        topic.save()
        return topic

    def create_message(idx: int, topic, position, banner = None):
        message = Message(
            type = 'message',
            enabled = True,
            publish = datetime.date(2016 + idx // 12, 1 + idx % 12, 1),
            title_tc = f'Message {idx} TC',
            title_sc = f'Message {idx} SC',
            author_tc = f'Author {idx} TC',
            author_sc = f'Author {idx} SC',
            banner_tc = banner,
            banner_sc = banner,
            position = position,
            parent = topic,
        )
        message.save()
        return message

    def create_parent_menu_item(idx: int, page = None):
        menu_item = ParentMenuItem(
            position = idx - 1,
            enabled = True,
            page = page,
            title_tc = f'Menu {idx} TC',
            title_sc = f'Menu {idx} SC',
        )
        menu_item.save()
        return menu_item

    def create_child_menu_item(idx: int, parent, position, page = None):
        menu_item = ChildMenuItem(
            parent = parent,
            position = position,
            enabled = True,
            page = page,
            title_tc = f'Submenu {idx} TC',
            title_sc = f'Submenu {idx} SC',
        )
        menu_item.save()
        return menu_item

    def create_promotion(idx: int, lang, position, page):
        promotion = Promotion(
            position = position,
            language = HomePage.objects.get(pk=lang),
            alt = f'Hint {idx}',
            title = f'Promotion {idx}',
            description = f'Description {idx}',
            page = page,
        )
        with download_random_image(250, 250) as f:
            promotion.image.save(random_image_name(), File(f))

        promotion.save()
        return promotion

    def create_banner(idx: int):
        banner = Banner(
            title = f'Banner {idx}',
        )
        with download_random_image(1920, 1080) as f:
            banner.image.save(random_image_name(), File(f))
        banner.save()
        return banner

    def create_home_banner(lang, position, banner, page = None):
        home_banner = HomeBanner(
            language = HomePage.objects.get(pk=lang),
            position = position,
            banner = banner,
            target_page = page,
        )
        home_banner.save()
        return home_banner

    banner1 = create_banner(1)
    banner2 = create_banner(2)
    banner3 = create_banner(3)
    topic1 = create_topic(1)
    topic2 = create_topic(2, banner3, True)
    message1 = create_message(1, topic1, 0, banner1)
    message2 = create_message(2, topic1, 1)
    message3 = create_message(3, topic2, 0)
    message4 = create_message(4, topic2, 1)
    home_banner1 = create_home_banner('tc', 0, banner1, message1)
    home_banner2 = create_home_banner('tc', 1, banner2, message2)
    home_banner3 = create_home_banner('sc', 0, banner1, topic1)
    promotion1 = create_promotion(1, 'tc', 0, message1)
    promotion2 = create_promotion(2, 'tc', 1, message2)
    promotion3 = create_promotion(3, 'tc', 2, message1)
    promotion4 = create_promotion(4, 'tc', 3, message2)
    promotion5 = create_promotion(5, 'sc', 0, message1)
    promotion6 = create_promotion(6, 'sc', 1, message2)
    promotion7 = create_promotion(7, 'sc', 2, message1)
    promotion8 = create_promotion(8, 'sc', 3, message2)
    menu_item1 = create_parent_menu_item(1)
    menu_item2 = create_parent_menu_item(2, topic1)
    menu_item3 = create_parent_menu_item(3, topic2)
    submenu_item1 = create_child_menu_item(1, menu_item1, 0, message1)
    submenu_item2 = create_child_menu_item(2, menu_item1, 1)
    submenu_item3 = create_child_menu_item(3, menu_item2, 0, message2)
