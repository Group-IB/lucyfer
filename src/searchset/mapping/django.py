from typing import List

from .base import MappingValue, Mapping


class DjangoMappingValue(MappingValue):
    def _get_values(self, qs, prefix: str) -> List[str]:
        result_qs = qs.filter(**{'{}__icontains'.format(self.sources[0]): prefix}).\
            values_list(self.sources[0], flat=True).distinct()

        other_qss = [
            qs.filter(**{'{}__icontains'.format(source): prefix}).values_list(source, flat=True).distinct()
            for source in self.sources[1:]
        ]

        if other_qss:
            result_qs = result_qs.union(*other_qss)

        return list(set(result_qs))


class DjangoMapping(Mapping):
    _value_class = DjangoMappingValue
