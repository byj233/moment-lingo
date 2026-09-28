import re
import time
from datetime import timezone, timedelta, datetime
from typing import Any


def _to_lower_camel_case(text: str) -> str:
    parts = text.split('_')

    if len(parts) == 1:
        return parts[0]

    camel_case = ''
    for part in parts:
        if part:
            if camel_case:
                camel_case += part.title()
            else:
                camel_case += part
    return camel_case


def to_lower_camel(item: Any) -> Any:
    if isinstance(item, dict):
        n_item = {}
        for key, value in item.items():
            n_item[_to_lower_camel_case(str(key))] = to_lower_camel(value)
        return n_item
    if isinstance(item, list):
        return [to_lower_camel(value) for value in item]
    if isinstance(item, tuple):
        return tuple(to_lower_camel(value) for value in item)
    return item


def _split_camel_case(camel_case: str) -> str:
    result = []
    for i, char in enumerate(camel_case):
        if i > 0 and char.isupper():
            result.append(' ')
        result.append(char.lower())
    return ''.join(result)


def convert_camel_case_in_text(text: str) -> str:
    pattern = re.compile(r'[a-z]+[A-Z][a-zA-Z]*|[A-Z][a-zA-Z]*')
    result = []
    last_end = 0

    for match in pattern.finditer(text):
        start = match.start()
        end = match.end()
        result.append(text[last_end:start])
        camel_case = match.group()
        converted = _split_camel_case(camel_case)
        result.append(converted)
        last_end = end
    result.append(text[last_end:])
    return ''.join(result)


def timestamp() -> int:
    return int(time.time() * 1000)


def beijing_time() -> str:
    beijing_tz = timezone(timedelta(hours=8))
    beijing_dt = datetime.now(beijing_tz)
    return beijing_dt.strftime("%Y-%m-%d %H:%M:%S")
