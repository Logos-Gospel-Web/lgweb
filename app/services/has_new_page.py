from datetime import datetime
from django.utils.timezone import get_current_timezone

from ..models import Page

def _check_past_page_count():
    now = datetime.now(tz=get_current_timezone())
    return Page.objects.filter(enabled=True, publish__lte=now).count()

_count = _check_past_page_count()

def check_has_new_page():
    global _count
    current_count = _check_past_page_count()
    has_new = _count != current_count
    _count = current_count
    return has_new
