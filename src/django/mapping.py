from src.base.mapping import MappingValue, Mapping


class DjangoMappingValue(MappingValue):
    def _get_values(self, prefix):
        raise NotImplementedError()


class DjangoMapping(Mapping):
    _value_class = DjangoMappingValue
