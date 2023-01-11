from django.db.models import Prefetch
from ..models import with_lang, ParentMenuItem, ChildMenuItem, Message

def get_menu():
    return ParentMenuItem.objects\
        .with_page_url()\
        .prefetch_related(
            Prefetch(
                'children',
                queryset=ChildMenuItem.objects\
                    .with_page_url()\
                    .filter(enabled=True))
        )\
        .filter(enabled=True)

def get_messages(lang, now, with_parent=True):
    res = Message.objects\
            .filter(enabled=True, publish__lte=now)\
            .exclude(**{ with_lang('title', lang): '' })

    if with_parent:
        return res.select_related('parent')\
            .filter(parent__enabled=True, parent__publish__lte=now)\
            .exclude(**{ with_lang('parent__title', lang): '' })

    return res
