from typing import Dict, List

from lucyparser.tree import Operator


class BaseSearchField:
    """
    Base Field class for including in SearchSet classes
    """

    DEFAULT_LOOKUP: str
    OPERATOR_TO_LOOKUP: Dict[Operator, str] = dict()

    def __init__(self, sources=None, exclude_sources_from_mapping=False, *args, **kwargs):
        sources = list() if sources is None else sources
        self.sources = set(sources)

        self.exclude_sources_from_mapping = exclude_sources_from_mapping

    def cast_value(self, value: str):
        """
        Method for value casting if it necessary
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


def negate_query_if_necessary(func):
    """
    Decorator to invert query if conditions operator was NEQ
    """
    def wrapper(self, condition):
        query = func(self, condition)
        if condition.operator == Operator.NEQ:
            query = query.__invert__()
        return query
    return wrapper
