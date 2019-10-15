from typing import List

from django.db.models.fields.related import ForeignKey

from .base import SearchHelperMixin
from ...searchset.mapping import DjangoMapping


class DjangoSearchHelperMixin(SearchHelperMixin):
    _mapping_class = DjangoMapping

    @classmethod
    def _get_raw_mapping(cls) -> List[str]:
        return [field.name for field in cls.Meta.model._meta.fields if not isinstance(field, ForeignKey)]
