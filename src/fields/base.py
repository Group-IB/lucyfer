from typing import Dict, List

from lucyparser.tree import Operator


class BaseSearchField:
    """
    Base Field class for including in SearchSet classes
    """

    DEFAULT_LOOKUP: str
    OPERATOR_TO_LOOKUP: Dict[Operator, str] = dict()
    _default_get_available_values_method = None

    def __init__(self, sources=None,
                 exclude_sources_from_mapping=False,
                 show_suggestions=True,
                 get_available_values_method=None,
                 *args, **kwargs):

        sources = list() if sources is None else sources
        self.sources = list(set(sources))

        self.exclude_sources_from_mapping = exclude_sources_from_mapping
        self.show_suggestions = show_suggestions
        self._get_available_values_method = get_available_values_method

    def cast_value(self, value: str):
        """
        Method for value casting if it necessary (or for ex. for search replaces)
        """
        return value

    def get_lookup(self, operator) -> str:
        """
        Returns lookup for searching
        """
        return self.OPERATOR_TO_LOOKUP.get(operator, self.DEFAULT_LOOKUP)

    def get_sources(self, field_name) -> List[str]:
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

    def get_available_values_method(self):
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
