from typing import List


def escape_quotes(values: List[str]) -> List[str]:
    try:
        values = [v.replace("'", "\\'").replace('"', '\\"') for v in values]
    except (AttributeError, TypeError):  # if value is not str
        pass
    return values
