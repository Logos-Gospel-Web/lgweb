from django.db.models import Prefetch, Q
from ..models import with_lang, ParentMenuItem, ChildMenuItem, Message

def get_menu(now):
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

def get_messages(lang, now, with_parent=True):
    res = Message.objects\
            .filter(enabled=True, publish__lte=now)\
            .exclude(**{ with_lang('title', lang): '' })

    if with_parent:
        return res.select_related('parent')\
            .filter(parent__enabled=True, parent__publish__lte=now)\
            .exclude(**{ with_lang('parent__title', lang): '' })

    return res
