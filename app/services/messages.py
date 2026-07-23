from ..lang import with_lang
from ..models import Message

def get_messages(lang, now, with_parent=True):
    res = Message.objects\
            .filter(enabled=True, publish__lte=now)\
            .exclude(**{ with_lang('title', lang): '' })

    if with_parent:
        return res.select_related('parent')\
            .filter(parent__enabled=True, parent__publish__lte=now)\
            .exclude(**{ with_lang('parent__title', lang): '' })

    return res
