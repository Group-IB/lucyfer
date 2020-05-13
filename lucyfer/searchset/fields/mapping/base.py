from itertools import islice
from typing import List

from django.core.cache import cache

from lucyfer.settings import lucyfer_settings


class MappingMixin:
    """
    Class provides interface to get search helpers for field by some prefix with cache
    """

    def get_values(self,
                   qs,
                   model_name: str,
                   escape_quotes_in_suggestions: bool,
                   prefix: str = '',
                   cache_key: str = "DEFAULT_KEY") -> List[str]:
        if not self.show_suggestions:
            return list()

        if not (self.use_cache_for_suggestions and lucyfer_settings.CACHE_SEARCH_VALUES):
            return self._get_parsed_values(qs=qs, prefix=prefix, escape_quotes_in_suggestions=escape_quotes_in_suggestions)

        key = f"LUCYFER__{model_name}__{cache_key}__{prefix}"

        if not cache.get(key):
            values = self._get_parsed_values(qs=qs, prefix=prefix, escape_quotes_in_suggestions=escape_quotes_in_suggestions)

            if len(prefix) < lucyfer_settings.CACHE_VALUES_MIN_LENGTH:
                return values

            cache.set(key, values, lucyfer_settings.CACHE_TIME)

        return cache.get(key)

    def _get_parsed_values(self, qs, prefix: str, escape_quotes_in_suggestions: bool) -> List[str]:
        values = self._get_available_values(qs=qs, prefix=prefix)

        if escape_quotes_in_suggestions:
            try:
                values = [v.replace("'", "\\'").replace('"', '\\"') for v in values]
            except (AttributeError, TypeError):  # if value is not str
                pass

        return values

    def _get_available_values(self, qs, prefix: str) -> List[str]:
        method = self.get_available_values_method()

        if callable(method):
            available_values = method(**self._available_values_method_kwargs)
            values = (v for v in available_values if prefix in v)
        else:
            values = self._get_values(qs, prefix)

        return list(islice(values, lucyfer_settings.CACHE_MAX_VALUES_COUNT_FOR_ONE_PREFIX))

    def _get_values(self, qs, prefix: str) -> List[str]:
        raise NotImplementedError()
