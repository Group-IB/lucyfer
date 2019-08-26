from typing import List

from ..base.searchhelper import SearchHelperMixin
from ..django.mapping import DjangoMapping


class DjangoSearchHelperMixin(SearchHelperMixin):
    _mapping_class = DjangoMapping

    @classmethod
    def _get_raw_mapping(cls) -> List[str]:
        return [field.name for field in cls.Meta.model._meta.fields]
