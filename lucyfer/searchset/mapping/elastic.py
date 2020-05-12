from lucyfer.searchset.mapping.base import Mapping
from lucyfer.searchset.mapping.values import ElasticMappingValue


class ElasticMapping(Mapping):
    _value_class = ElasticMappingValue
