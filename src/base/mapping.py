from collections import OrderedDict
from typing import Type, Dict, List


class MappingValue:
    """
    Class provides interface to get search helpers for field by some prefix with cache
    """
    name: str
    sources: List[str]

    _cached_values: Dict[str, List[str]]
    _max_cached_values_by_prefix = 10

    def __init__(self, name: str, sources=None):
        self.name = name
        self.sources = sources if sources is not None else [name]

    def get_values(self, model, prefix='') -> List[str]:
        if self._cached_values is None:
            self._cached_values = dict()

        if not self._cached_values.get(prefix):
            self._cached_values[prefix] = self._get_values(model, prefix)

        return self._cached_values.get(prefix, list())

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

    def add_value(self, name: str, **kwargs):
        self.update({name: self._value_class(name=name, **kwargs)})

    def update_raw_sources(self, raw_sources: List[str]):
        self.update({source: self._value_class(name=source) for source in raw_sources})

    def update_named_sources(self, name_to_sources: Dict[str, str]):
        self.update({name: self._value_class(name=name, sources=source) for name, source in name_to_sources.items()})

    def get_values(self, field_name: str, prefix: str) -> List[str]:
        """
        Add values helpers for field by prefix
        """
        if field_name not in self:
            return list()

        return self[field_name].get_values(model=self.model, prefix=prefix)
