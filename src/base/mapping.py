from collections import OrderedDict
from typing import Type, Dict, List, Optional


class MappingValue:
    """
    Class provides interface to get search helpers for field by some prefix with cache
    """
    name: str
    sources: List[str]

    _cached_values: Optional[Dict[str, List[str]]] = None
    _max_cached_values_by_prefix = 10

    def __init__(self, name: str, sources=None, get_available_values_method=None, show_suggestions=True):
        self.name = name
        self.sources = sources if sources else [name]

        self.get_available_values_method = get_available_values_method

        self.show_suggestions = show_suggestions

    def get_values(self, model, prefix='') -> List[str]:
        if not self.show_suggestions:
            return list()

        if self._cached_values is None:
            self._cached_values = dict()

        if not self._cached_values.get(prefix):
            self._cached_values[prefix] = self._get_values(model, prefix)

        result = self._cached_values.get(prefix, list())
        if self.get_available_values_method is not None:
            available_values = self.get_available_values_method()
            result = [value for value in result if value in available_values]

        return result[:self._max_cached_values_by_prefix]

    def _get_values(self, model, prefix: str) -> List[str]:
        raise NotImplementedError()


class Mapping(OrderedDict):
    """
    Mapping as a dict
    """

    def __init__(self, model, *args, **kwargs):
        self.model = model
        super().__init__(*args, **kwargs)

    _value_class: Type[MappingValue]
    _model = None

    def add_value(self, name: str, sources=None, get_available_values_method=None, show_suggestions=True):
        if name not in self:
            self.update({name: self._value_class(name=name,
                                                 sources=sources,
                                                 get_available_values_method=get_available_values_method,
                                                 show_suggestions=show_suggestions,
                                                 )})

    def get_values(self, field_name: str, prefix: str) -> List[str]:
        """
        Add values helpers for field by prefix
        """
        if field_name not in self:
            return list()

        return self[field_name].get_values(model=self.model, prefix=prefix)
