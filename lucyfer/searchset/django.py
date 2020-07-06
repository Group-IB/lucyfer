from typing import List, Dict

from django.core.exceptions import FieldError
from django.db.models import ForeignKey, AutoField, BooleanField, BigAutoField, BigIntegerField, FloatField, \
    IntegerField, NullBooleanField, PositiveIntegerField, PositiveSmallIntegerField, DateTimeField, DateField

from lucyfer.searchset.base import BaseSearchSet
from lucyfer.searchset.fields.django import DjangoSearchField, DjangoSearchFieldWithoutWildcard, \
    default_django_field_types_to_fields
from lucyfer.searchset.utils import FieldType
from lucyfer.parser import LuceneToDjangoParserMixin
from lucyfer.utils import LuceneSearchException


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
    DateTimeField: FieldType.TIMESTAMP,
    DateField: FieldType.TIMESTAMP,
}


class DjangoSearchSet(LuceneToDjangoParserMixin, BaseSearchSet):
    _field_base_class = DjangoSearchFieldWithoutWildcard
    _default_field = DjangoSearchField
    _field_class_for_default_searching = DjangoSearchField

    _field_type_to_field_class = default_django_field_types_to_fields
    _raw_type_to_field_type = django_model_field_to_field_type

    @classmethod
    def filter(cls, queryset, search_terms, raise_exception=False):
        query = cls.parse(raw_expression=search_terms)
        try:
            return queryset.filter(query)
        except FieldError:
            if raise_exception:
                raise LuceneSearchException()

            return queryset.none()

    @classmethod
    def _get_raw_mapping(cls) -> Dict[str, FieldType]:
        return {field.name: cls._raw_type_to_field_type.get(field.__class__)
                for field in cls._meta.model._meta.fields
                if not isinstance(field, ForeignKey)}

    @classmethod
    def get_fields_sources(cls) -> List[str]:
        """
        Returns sources for field defined in searchset class
        """
        sources = []
        for name, field in cls.storage.field_name_to_field.items():
            sources.extend(field.sources)
        return sources
