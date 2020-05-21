from typing import List

from django.db.models import QuerySet

from lucyfer.searchset.fields.mapping.base import MappingMixin


class DjangoMappingMixin(MappingMixin):
    def prepare_qs_for_suggestions(self, qs, prefix: str):
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

        return first.union(*qss)

    def get_suggestions_from_prepared_qs(self, qs, prefix: str) -> List[str]:
        return list(set(qs))
