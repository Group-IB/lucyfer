from typing import List, Optional

from django.core.exceptions import FieldError
from django.db.models import ForeignKey

from ..searchset.fields.django import DjangoSearchField, DjangoSearchFieldWithoutWildcard
from ..searchset.mapping import DjangoMapping
from ..parser import LuceneToDjangoParserMixin

from .base import BaseSearchSet
from .fields.django import default_django_field_types_to_fields


class DjangoSearchSet(LuceneToDjangoParserMixin, BaseSearchSet):
    _field_base_class = DjangoSearchFieldWithoutWildcard
    _default_field = DjangoSearchField
    _field_type_to_field_class = default_django_field_types_to_fields

    _field_sources: Optional[List[str]] = None

    @classmethod
    def filter(cls, queryset, search_terms):
        query = cls.parse(raw_expression=search_terms)
        try:
            return queryset.filter(query)
        except FieldError:
            return queryset.none()

    # for search helper

    _mapping_class = DjangoMapping

    @classmethod
    def _get_raw_mapping(cls):
        return [field.name for field in cls.Meta.model._meta.fields if not isinstance(field, ForeignKey)]

    @classmethod
    def get_fields_sources(cls) -> List[str]:
        """
        Returns sources for field defined in searchset class
        """
        if cls._field_sources is None:
            cls._field_sources = list()

            for name, _cls in cls.__dict__.items():
                if isinstance(_cls, cls._field_base_class):
                    cls._field_sources.extend(_cls.get_sources(name))

        return cls._field_sources
