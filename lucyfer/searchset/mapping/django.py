from lucyfer.searchset.mapping.base import Mapping
from lucyfer.searchset.mapping.values import DjangoMappingValue


class DjangoMapping(Mapping):
    _value_class = DjangoMappingValue
