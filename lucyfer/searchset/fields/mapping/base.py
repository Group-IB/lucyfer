from itertools import islice
from typing import List

from django.core.cache import cache

from lucyfer.searchset.fields.mapping.utils import escape_quotes, ignore_empty_values, custom_sorted
from lucyfer.settings import lucyfer_settings


class MappingMixin:
    """
    Class provides interface to get values-suggestions for field by some prefix with cache
    """

    def get_values(self,
                   qs,
                   model_name: str,
                   escape_quotes_in_suggestions: bool,
                   prefix: str = '',
                   cache_key: str = "DEFAULT_KEY",
                   max_return_suggestions_count: int = lucyfer_settings.CACHE_MAX_VALUES_COUNT_FOR_ONE_PREFIX,
                   allow_empty_values: bool = lucyfer_settings.ALLOW_EMPTY_SUGGESTIONS,
                   sort_values: bool = True) -> List[str]:
        if not self.show_suggestions:
            return list()

        return_sorted_if_need = lambda x: custom_sorted(x) if sort_values else x

        key = f"LUCYFER__{model_name}__{cache_key}__{prefix}"

        # possibly the values has been cached already
        if self._is_prefix_may_be_cached(prefix=prefix) and cache.get(key):
            return return_sorted_if_need(cache.get(key))

        values = self._get_values(qs=qs, prefix=prefix,
                                  escape_quotes_in_suggestions=escape_quotes_in_suggestions,
                                  allow_empty_values=allow_empty_values)

        # if None we will return ALL found values, else needed count
        if max_return_suggestions_count is not None:
            values = list(islice(values, max_return_suggestions_count))

        # next we have to cache it
        if self._is_prefix_may_be_cached(prefix=prefix):
            cache.set(key, values, lucyfer_settings.CACHE_TIME)

        return return_sorted_if_need(values)

    def prepare_qs_for_suggestions(self, qs, prefix: str):
        """
        Process qs or search. Add aggregation things to use it in later for values getting
        """
        raise NotImplementedError()

    def get_suggestions_from_prepared_qs(self, qs, prefix: str):
        """
        Execute the qs or search and get raw values from it
        """
        raise NotImplementedError()

    def _get_values(self,
                    qs,
                    prefix: str,
                    escape_quotes_in_suggestions: bool,
                    allow_empty_values: bool) -> List[str]:
        """
        Returns all possible values (NOT SLICED)
        """
        method = self.get_available_values_method()

        if callable(method):
            prefix_lower = prefix.lower()
            available_values = method(**self._available_values_method_kwargs)
            values = list(set((v for v in available_values if prefix_lower in v.lower())))
        else:
            qs = self.prepare_qs_for_suggestions(qs=qs, prefix=prefix)
            values = self.get_suggestions_from_prepared_qs(qs=qs, prefix=prefix)

        if not allow_empty_values:
            values = ignore_empty_values(values)

        if escape_quotes_in_suggestions:
            values = escape_quotes(values)

        return values

    def _is_prefix_may_be_cached(self, prefix):
        return lucyfer_settings.CACHE_SEARCH_VALUES and \
               self.use_cache_for_suggestions and \
               len(prefix) >= lucyfer_settings.CACHE_VALUES_MIN_LENGTH
