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
                 use_field_class_for_sources: bool = False,
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

        for k, v in kwargs.items():
            assert not k in dir(self), f'Kwarg "{k}" clashes with another class attribute'
            setattr(self, k, v)

    def _contribute_to_class(self, field_name):
        """
        in searchset metaclass we have to contribute field name to field class if it was defined by user
        """
        self.sources = self.sources or [field_name]

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
        Be careful: in the default field you MUST use that method instead of self.sources usage.
        That because you have no idea about field name you've got for query generation
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
