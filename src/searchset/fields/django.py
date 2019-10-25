from django.db.models import Q
from lucyparser.tree import Operator

from ...searchset.utils import FieldType
from ...utils import LuceneSearchCastValueException

from .base import BaseSearchField, negate_query_if_necessary


class DjangoSearchFieldWithoutWildcard(BaseSearchField):
    DEFAULT_LOOKUP = "icontains"

    def create_query_for_sources(self, condition):
        query = Q()

        lookup = self.get_lookup(condition.operator)
        value = self.cast_value(condition.value)

        for source in self.get_sources(condition.name):
            query = query | Q(**{"{}__{}".format(source, lookup): value})
        return query

    @negate_query_if_necessary
    def get_query(self, condition):
        if self.match_all(value=condition.value):
            return None

        return self.create_query_for_sources(condition=condition)


class DjangoSearchField(DjangoSearchFieldWithoutWildcard):
    DEFAULT_LOOKUP = "iexact"

    def create_query_for_sources(self, condition):
        value = self.cast_value(condition.value)

        if value.startswith("*") and value.endswith("*"):
            lookup = "icontains"
            value = value[1:-1]
        elif value.startswith("*"):
            lookup = "iendswith"
            value = value[1:]
        elif value.endswith("*"):
            value = value[:-1]
            lookup = "istartswith"
        else:
            return super().create_query_for_sources(condition)

        if not value:
            return None

        sources = self.get_sources(condition.name)

        query = Q()

        for source in sources:
            query = query | Q(**{"{}__{}".format(source, lookup): value})

        return query


class DjangoCharField(DjangoSearchField):
    OPERATOR_TO_LOOKUP = {
        Operator.EQ: "icontains",
        Operator.NEQ: "iexact",
    }


class DjangoNumberField(DjangoSearchFieldWithoutWildcard):
    OPERATOR_TO_LOOKUP = {
        Operator.GTE: "gte",
        Operator.LTE: "lte",
        Operator.GT: "gt",
        Operator.LT: "lt",
        Operator.EQ: "exact",
        Operator.NEQ: "exact",
    }


class DjangoIntegerField(DjangoNumberField):
    def cast_value(self, value):
        try:
            return int(value)
        except (ValueError, TypeError):
            raise LuceneSearchCastValueException()


class DjangoFloatField(DjangoNumberField):
    def cast_value(self, value):
        try:
            return float(value)
        except (ValueError, TypeError):
            raise LuceneSearchCastValueException()


class DjangoBooleanField(DjangoSearchFieldWithoutWildcard):
    OPERATOR_TO_LOOKUP = {
        Operator.EQ: "exact",
        Operator.NEQ: "exact",
    }

    _values = {"true": True, "false": False}
    _default_get_available_values_method = _values.keys

    def cast_value(self, value):
        value = value.lower()
        if value in self._values:
            return self._values[value]

        raise LuceneSearchCastValueException()


class DjangoNullBooleanField(DjangoBooleanField):
    _values = {"true": True, "false": False, "null": None}
    _default_get_available_values_method = _values.keys


default_django_field_types_to_fields = {
    FieldType.INTEGER: DjangoIntegerField,
    FieldType.BOOLEAN: DjangoBooleanField,
    FieldType.NULL_BOOLEAN: DjangoNullBooleanField,
    FieldType.FLOAT: DjangoFloatField
}
