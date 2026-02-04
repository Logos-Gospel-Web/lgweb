def format_author(text: str, format: str):
    is_formattable = bool(format) and format.format('') != format
    if is_formattable:
        return format.format(text) if text else ''
    else:
        return text or format or ''
