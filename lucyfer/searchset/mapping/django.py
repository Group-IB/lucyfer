from typing import List

from lucyfer.searchset.mapping.base import MappingValue, Mapping


class DjangoMappingValue(MappingValue):
    def _get_values(self, qs, prefix: str) -> List[str]:
        if prefix:
            qss = [
                qs.filter(**{'{}__icontains'.format(source): prefix}).values_list(source, flat=True).distinct()
                for source in self.sources
            ]
        else:
            qss = [
                qs.values_list(source, flat=True).distinct()
                for source in self.sources
            ]

        if len(qss) == 0:
            return []

        if len(qss) > 1:
            qss = qss.pop().union(*qss)

        return list(set(qss))


class DjangoMapping(Mapping):
    _value_class = DjangoMappingValue
