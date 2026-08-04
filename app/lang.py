from typing import Literal

type Language = Literal['tc', 'sc']

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

def to_locale(lang: Language) -> str:
    return _TO_LOCALE[lang]

def to_lang_tag(lang: Language) -> str:
    return _TO_LANG_TAG[lang]

def to_lang(locale: str) -> Language:
    return _FROM_LOCALE[locale]

def with_lang(field: str, lang: Language):
    return f'{field}_{lang}'

def is_valid_language(language: str) -> bool:
    return language in LANGUAGES
