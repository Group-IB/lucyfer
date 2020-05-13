from typing import Dict, List, Optional, Callable, Any

from lucyparser.tree import Operator

from lucyfer.searchset.fields.mapping.base import MappingMixin
from lucyfer.settings import lucyfer_settings


class BaseSearchField(MappingMixin):
    """
    Base Field class for including in SearchSet classes
    """

    DEFAULT_LOOKUP: str
    OPERATOR_TO_LOOKUP: Dict[Operator, str] = dict()
    _default_get_available_values_method = None

    def __init__(self,
                 sources: Optional[List[str]] = None,
                 exclude_sources_from_mapping: bool = False,
                 show_suggestions: bool = True,
                 get_available_values_method: Optional[Callable[..., List[Any]]] = None,
                 available_values_method_kwargs: Optional[Dict[str, Any]] = None,
                 use_field_class_for_sources: bool = True,
                 use_cache_for_suggestions: bool = None,
                 *args, **kwargs):

        sources = list() if sources is None else sources
        self.sources = list(set(sources))

        self.exclude_sources_from_mapping = exclude_sources_from_mapping
        self.show_suggestions = show_suggestions
        self.use_field_class_for_sources = use_field_class_for_sources
        self._get_available_values_method = get_available_values_method
        self._available_values_method_kwargs = available_values_method_kwargs or {}

        if use_cache_for_suggestions is None:
            self.use_cache_for_suggestions = lucyfer_settings.CACHE_SEARCH_VALUES
        else:
            self.use_cache_for_suggestions = use_cache_for_suggestions

    def cast_value(self, value: str):
        """
        Method for value casting if it necessary (or for ex. for search replaces)
        """
        return value

    def get_lookup(self, operator: Operator) -> str:
        """
        Returns lookup for searching
        """
        return self.OPERATOR_TO_LOOKUP.get(operator, self.DEFAULT_LOOKUP)

    def get_sources(self, field_name: str) -> List[str]:
        """
        Returns sources list
        """
        return self.sources or [field_name]

    def get_query(self, condition):
        """
        Returns Q object with query
        """
        raise NotImplementedError()

    def match_all(self, value) -> bool:
        """
        Check filtration necessary
        """
        return value == "*"

    def get_available_values_method(self) -> Optional[Callable[..., List[Any]]]:
        return self._get_available_values_method or self._default_get_available_values_method


def negate_query_if_necessary(func):
    """
    Decorator to invert query if conditions operator was NEQ
    """
    def wrapper(self, condition):
        query = func(self, condition)

        if query is not None and condition.operator == Operator.NEQ:
            query = query.__invert__()

        return query
    return wrapper
