EMPTY_STRING_PLACEHOLDER = '[__EMPTY__]'
REPLACEMENTS = {
    ':': '[__COLON__]'
}

def escape(value: str) -> str:
    value = value.strip()
    if value == '':
        return EMPTY_STRING_PLACEHOLDER
    for user, file in REPLACEMENTS.items():
        value = value.replace(user, file)
    return value


def unescape(value: str) -> str:
    if value == EMPTY_STRING_PLACEHOLDER:
        return ''
    for user, file in REPLACEMENTS.items():
        value = value.replace(file, user)
    return value
