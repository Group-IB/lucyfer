from typing import List

from src.base.searchhelper import SearchHelperMixin
from src.django.mapping import DjangoMapping


class DjangoSearchHelperMixin(SearchHelperMixin):
    _mapping_class = DjangoMapping

    @classmethod
    def _get_raw_mapping(cls) -> List[str]:
        return list(cls.Meta.model._meta.fields)
