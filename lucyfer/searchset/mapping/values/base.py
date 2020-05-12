from itertools import islice
from typing import List

from django.core.cache import cache

from lucyfer.settings import lucyfer_settings


class MappingValue:
    """
    Class provides interface to get search helpers for field by some prefix with cache
    """
    name: str
    sources: List[str]

    def __init__(self, name: str,
                 use_cache_for_suggestions: bool,
                 field_type=None,
                 sources=None,
                 show_suggestions=True,
                 get_available_values_method=None,
                 escape_quotes_in_suggestions=True):
        self.name = name
        self.field_type = field_type
        self.sources = sources if sources else [name]
        self.show_suggestions = show_suggestions
        self.get_available_values_method = get_available_values_method
        self.escape_quotes_in_suggestions = escape_quotes_in_suggestions
        self.use_cache_for_suggestions = use_cache_for_suggestions

    def get_values(self, qs, model_name, prefix='', cache_key=None) -> List[str]:
        if not self.show_suggestions:
            return list()

        if not (self.use_cache_for_suggestions and lucyfer_settings.CACHE_SEARCH_VALUES):
            return self._get_parsed_values(qs=qs, prefix=prefix)

        key = f"LUCYFER__{model_name}__{cache_key}__{prefix}"

        if not cache.get(key):
            values = self._get_parsed_values(qs=qs, prefix=prefix)

            if len(prefix) < lucyfer_settings.CACHE_VALUES_MIN_LENGTH:
                return values

            cache.set(key, values, lucyfer_settings.CACHE_TIME)

        return cache.get(key)

    def _get_parsed_values(self, qs, prefix):
        values = self._get_available_values(qs=qs, prefix=prefix)

        if self.escape_quotes_in_suggestions:
            try:
                values = [v.replace("'", "\\'").replace('"', '\\"') for v in values]
            except (AttributeError, TypeError):  # if value is not str
                pass

        return values

    def _get_available_values(self, qs, prefix):
        if callable(self.get_available_values_method):
            available_values = self.get_available_values_method()
            values = (v for v in available_values if prefix in v)
        else:
            values = self._get_values(qs, prefix)

        return list(islice(values, lucyfer_settings.CACHE_MAX_VALUES_COUNT_FOR_ONE_PREFIX))

    def _get_values(self, qs, prefix: str) -> List[str]:
        raise NotImplementedError()
