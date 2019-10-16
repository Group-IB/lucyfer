from typing import List, Optional, Dict

from django.core.exceptions import FieldError
from django.db.models import ForeignKey, AutoField, BooleanField, BigAutoField, BigIntegerField, FloatField, \
    IntegerField, NullBooleanField, PositiveIntegerField, PositiveSmallIntegerField

from ..searchset.fields.django import DjangoSearchField, DjangoSearchFieldWithoutWildcard
from ..searchset.mapping import DjangoMapping
from ..searchset.utils import FieldType
from ..parser import LuceneToDjangoParserMixin

from .base import BaseSearchSet
from .fields.django import default_django_field_types_to_fields


django_model_field_to_field_type = {
    AutoField: FieldType.INTEGER,
    BigAutoField: FieldType.INTEGER,
    BigIntegerField: FieldType.INTEGER,
    BooleanField: FieldType.BOOLEAN,
    FloatField: FieldType.FLOAT,
    IntegerField: FieldType.INTEGER,
    NullBooleanField: FieldType.NULL_BOOLEAN,
    PositiveIntegerField: FieldType.INTEGER,  # todo positive integer field
    PositiveSmallIntegerField: FieldType.INTEGER,
}


class DjangoSearchSet(LuceneToDjangoParserMixin, BaseSearchSet):
    _field_base_class = DjangoSearchFieldWithoutWildcard
    _default_field = DjangoSearchField

    _field_type_to_field_class = default_django_field_types_to_fields
    _django_model_field_to_field_type = django_model_field_to_field_type

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
    def _get_raw_mapping(cls) -> Dict[str, FieldType]:
        return {field.name: cls._django_model_field_to_field_type.get(field.__class__)
                for field in cls.Meta.model._meta.fields
                if not isinstance(field, ForeignKey)}

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
