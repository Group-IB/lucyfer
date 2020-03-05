from typing import List

from django.db.models import QuerySet
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

        if not qss:
            return []

        first = qss.pop()
        if not isinstance(first, QuerySet):
            return []

        return list(set(first.union(*qss)))


class DjangoMapping(Mapping):
    _value_class = DjangoMappingValue
