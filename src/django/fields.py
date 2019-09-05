from django.db.models import Q
from lucyparser.tree import Operator

from ..base.fields import BaseSearchField, negate_query_if_necessary
from ..utils import LuceneSearchCastValueException


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
    def create_query_for_sources(self, condition):
        value = self.cast_value(condition.value)

        if value.startswith("*") and value.endswith("*"):
            lookup = "icontains"
            value = value[1:-1]
        elif value.startswith("*"):
            lookup = "iendswith"
            value = value[1:]
        elif value.endswith("*"):
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


class CharField(DjangoSearchField):
    OPERATOR_TO_LOOKUP = {
        Operator.EQ: "icontains",
        Operator.NEQ: "iexact",
    }


class NumberField(DjangoSearchFieldWithoutWildcard):
    OPERATOR_TO_LOOKUP = {
        Operator.GTE: "gte",
        Operator.LTE: "lte",
        Operator.GT: "gt",
        Operator.LT: "lt",
        Operator.EQ: "exact",
        Operator.NEQ: "exact",
    }


class IntegerField(NumberField):
    def cast_value(self, value):
        try:
            return int(value)
        except (ValueError, TypeError):
            raise LuceneSearchCastValueException()


class FloatField(NumberField):
    def cast_value(self, value):
        try:
            return float(value)
        except (ValueError, TypeError):
            raise LuceneSearchCastValueException()


class BooleanField(DjangoSearchFieldWithoutWildcard):
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


class NullBooleanField(BooleanField):
    _values = {"true": True, "false": False, "null": None}
    _default_get_available_values_method = _values.keys
