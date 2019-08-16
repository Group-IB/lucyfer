from src.base.mapping import MappingValue, Mapping


class ElasticMappingValue(MappingValue):
    def _get_values(self, prefix):
        raise NotImplementedError()


class ElasticMapping(Mapping):
    _value_class = ElasticMappingValue
