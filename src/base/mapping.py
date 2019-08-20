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

    def __init__(self, name: str, sources=None, get_available_values_method=None):
        self.name = name
        self.sources = sources if sources else [name]
        self.get_available_values_method = get_available_values_method

    def get_values(self, model, prefix='') -> List[str]:
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

    def add_value(self, name: str, get_available_values_method=None, **kwargs):
        self.update({name: self._value_class(name=name,
                                             get_available_values_method=get_available_values_method,
                                             **kwargs)})

    def update_raw_sources(self, raw_sources: List[str], get_available_values_method=None):
        self.update({source: self._value_class(name=source, get_available_values_method=get_available_values_method)
                     for source in raw_sources
                     if source not in self})

    def get_values(self, field_name: str, prefix: str) -> List[str]:
        """
        Add values helpers for field by prefix
        """
        if field_name not in self:
            return list()

        return self[field_name].get_values(model=self.model, prefix=prefix)
