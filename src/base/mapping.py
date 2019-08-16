from collections import OrderedDict


class MappingValue:
    name = None
    sources = None
    _cached_values = None
    _max_cached_values_by_prefix = 10

    def __init__(self, name, sources=None):
        self.name = name
        self.sources = sources if sources is not None else [name]

    def get_values(self, prefix=''):
        if self._cached_values is None:
            self._cached_values = dict()
        elif prefix in self._cached_values:
            return self._cached_values[prefix]
        self._cached_values[prefix] = self._get_values(prefix)

    def _get_values(self, prefix):
        raise NotImplementedError()


class Mapping(OrderedDict):
    _value_class = None

    def add_value(self, name, **kwargs):
        self.update({name: self._value_class(name=name, **kwargs)})

    def update_raw_sources(self, raw_sources):
        self.update({source: self._value_class(name=source) for source in raw_sources})

    def update_named_sources(self, name_to_sources):
        self.update({name: self._value_class(name=name, sources=source) for name, source in name_to_sources.items()})
