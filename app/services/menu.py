from datetime import datetime
from django.core.cache import caches
from django.db.models import Prefetch
from ..models import ParentMenuItem, ChildMenuItem

_MENU_CACHE_KEY = '__MENU__'

def _get_menu(now: datetime):
    menu = ParentMenuItem.objects\
        .filter_disabled_item(now, True)\
        .prefetch_related(
            Prefetch(
                'children',
                queryset=ChildMenuItem.objects\
                    .filter_disabled_item(now, False))
        )\
        .all()
    return [item for item in menu if item.children.exists() or item.page is not None]

def get_menu(now: datetime, cache = True):
    if cache:
        return caches['components'].get_or_set(_MENU_CACHE_KEY, lambda: _get_menu(now))
    else:
        return _get_menu(now)
