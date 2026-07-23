from datetime import datetime
from django.utils.timezone import get_current_timezone

def _get_now():
    return datetime.now(tz=get_current_timezone())

_last_check = _get_now()
_count = None

def _check_past_page_count(now: datetime):
    from ..models import Page
    return Page.objects.filter(enabled=True, publish__lte=now).count()

def check_has_new_page():
    global _count, _last_check

    if _count is None:
        _count = _check_past_page_count(_last_check)

    _last_check = _get_now()
    current_count = _check_past_page_count(_last_check)
    has_new = _count != current_count
    _count = current_count
    return has_new
