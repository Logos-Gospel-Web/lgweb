import logging


logger = logging.getLogger(__name__)


def format_author(text: str | None, template: str | None) -> str:
    text = text or ''
    template = template or ''

    if not template:
        return text

    try:
        is_formattable = template.format('') != template
    except (IndexError, KeyError, ValueError):
        logger.warning('Invalid author format: %r', template)
        return text

    if not is_formattable:
        return text or template

    if not text:
        return ''

    try:
        return template.format(text)
    except (IndexError, KeyError, ValueError):
        logger.warning('Invalid author format: %r', template)
        return text
