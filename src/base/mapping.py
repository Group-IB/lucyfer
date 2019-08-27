from collections import OrderedDict, defaultdict
from typing import Type, Dict, List, Optional


class MappingValue:
    """
    Class provides interface to get search helpers for field by some prefix with cache
    """
    name: str
    sources: List[str]

    _cached_values: Optional[Dict[str, Dict[str, List[str]]]] = None
    _max_cached_values_by_prefix = 10

    def __init__(self, name: str, sources=None, get_available_values_method=None, show_suggestions=True):
        self.name = name
        self.sources = sources if sources else [name]

        self.get_available_values_method = get_available_values_method

        self.show_suggestions = show_suggestions

    def get_values(self, qs, prefix='', cache_key=None) -> List[str]:
        if not self.show_suggestions:
            return list()

        if self._cached_values is None:
            self._cached_values = defaultdict(dict)

        if not self._cached_values[cache_key].get(prefix):
            self._cached_values[cache_key][prefix] = self._get_values(qs, prefix)

        result = self._cached_values[cache_key].get(prefix, list())
        if self.get_available_values_method is not None:
            available_values = self.get_available_values_method()
            result = [value for value in result if value in available_values]

        return result[:self._max_cached_values_by_prefix]

    def _get_values(self, qs, prefix: str) -> List[str]:
        raise NotImplementedError()


class Mapping(OrderedDict):
    """
    Mapping as a dict
    """

    _value_class: Type[MappingValue]
    _model = None

    def __init__(self, model, *args, **kwargs):
        self.model = model
        super().__init__(*args, **kwargs)

    def add_value(self, name: str, sources=None, get_available_values_method=None, show_suggestions=True):
        if name not in self:
            self.update({name: self._value_class(name=name,
                                                 sources=sources,
                                                 get_available_values_method=get_available_values_method,
                                                 show_suggestions=show_suggestions,
                                                 )})

    def get_values(self, qs, field_name: str, prefix: str, cache_key="DEFAULT_KEY") -> List[str]:
        """
        Get values helpers for field by prefix

        :param qs: queryset with additional filters or els search
        :param field_name: field name for get values
        :param prefix: prefix for searching values
        :param cache_key: additional argument to use possibility to cache different values for different users for ex.

        :return: list of values
        """

        if field_name not in self:
            return list()

        return self[field_name].get_values(qs=qs, prefix=prefix, cache_key=cache_key)
