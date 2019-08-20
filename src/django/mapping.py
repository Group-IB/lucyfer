from typing import List

from src.base.mapping import MappingValue, Mapping


class DjangoMappingValue(MappingValue):
    def _get_values(self, model, prefix: str) -> List[str]:
        result_qs = model.objects.filter(**{'{}__icontains'.format(self.sources[0]): prefix}).\
            values_list(self.sources[0], flat=True).distinct()

        other_qss = [
            model.objects.filter(**{'{}__icontains'.format(source): prefix}).values_list(source, flat=True).distinct()
            for source in self.sources[1:]
        ]

        if other_qss:
            result_qs = result_qs.union(*other_qss)

        return list(set(result_qs))


class DjangoMapping(Mapping):
    _value_class = DjangoMappingValue
