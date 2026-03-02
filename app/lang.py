LANGUAGES = ('tc', 'sc')

LANGUAGE_NAMES = {
    'tc': '繁體',
    'sc': '简体',
}

_TO_LOCALE = {
    'tc': 'zh_TW',
    'sc': 'zh_CN',
}

_FROM_LOCALE = {
    'zh_TW': 'tc',
    'zh-tw': 'tc',
    'zh_CN': 'sc',
    'zh-cn': 'sc',
}

_TO_LANG_TAG = {
    'tc': 'zh-hant',
    'sc': 'zh-hans',
}

def to_locale(lang: str) -> str:
    return _TO_LOCALE[lang]

def to_lang_tag(lang: str) -> str:
    return _TO_LANG_TAG[lang]

def to_lang(locale: str) -> str:
    return _FROM_LOCALE[locale]

def with_lang(field: str, lang: str):
    return f'{field}_{lang}'
