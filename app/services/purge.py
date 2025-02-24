from datetime import datetime
from django.core.cache import caches
from django.utils.timezone import get_current_timezone

from ..models import Page

def _check_past_page_count():
    now = datetime.now(tz=get_current_timezone())
    return Page.objects.filter(enabled=True, publish__lte=now).count()

_count = _check_past_page_count()

def _purge():
    caches['default'].clear()
    caches['etag'].clear()

def purge_cache():
    global _count
    _count = _check_past_page_count()
    _purge()

def purge_cache_if_needed():
    global _count
    current_count = _check_past_page_count()
    if _count != current_count:
        _count = current_count
        _purge()
