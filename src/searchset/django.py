from django.core.exceptions import FieldError

from .base import BaseSearchSet
from ..searchset.fields.django import DjangoSearchField, DjangoSearchFieldWithoutWildcard
from ..parser import LuceneToDjangoParserMixin


class DjangoSearchSet(LuceneToDjangoParserMixin, BaseSearchSet):
    _field_base_class = DjangoSearchFieldWithoutWildcard
    _default_field = DjangoSearchField

    @classmethod
    def filter(cls, queryset, search_terms):
        query = cls.parse(raw_expression=search_terms)
        try:
            return queryset.filter(query)
        except FieldError:
            return queryset.none()
