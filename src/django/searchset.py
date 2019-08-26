from django.core.exceptions import FieldError

from ..base.searchset import BaseSearchSet
from ..django.fields import DjangoSearchField, DjangoSearchFieldWithoutWildcard
from ..django.parser import LuceneToDjangoParserMixin


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
