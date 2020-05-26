from typing import List

from lucyfer.settings import lucyfer_settings


def escape_quotes(values: List[str]) -> List[str]:
    try:
        values = [v.replace("'", "\\'").replace('"', '\\"') for v in values]
    except (AttributeError, TypeError):  # if value is not str
        pass
    return values


def ignore_empty_values(values: List[str]) -> List[str]:
    return [v for v in values if v is not lucyfer_settings.EMPTY_SUGGESTIONS_VALUES]
