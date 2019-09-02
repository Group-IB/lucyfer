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
        wildcard_parts = self.cast_value(condition.value).split("*")

        parts_count = len(wildcard_parts)

        if parts_count == 1:
            return super().create_query_for_sources(condition)

        source_to_query = {source: Q() for source in self.get_sources(condition.name)}

        def update_query(lookup, value):
            for source in source_to_query:
                source_to_query[source] = source_to_query[source] & Q(**{"{}__{}".format(source, lookup): value})

        for index, w_part in enumerate(wildcard_parts):
            if w_part:
                if index == 0:
                    update_query(lookup="istartswith", value=w_part)
                    continue

                elif index == (parts_count - 1):
                    update_query(lookup="iendswith", value=w_part)
                    continue

                else:
                    update_query(lookup="icontains", value=w_part)
                    continue

        final_query = Q()
        for query in source_to_query.values():
            final_query = final_query & query

        return final_query


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
    _default_available_values = list(_values.values())

    def cast_value(self, value):
        value = value.lower()
        if value in self._values:
            return self._values[value]

        raise LuceneSearchCastValueException()


class NullBooleanField(BooleanField):
    _values = {"true": True, "false": False, "null": None}
    _default_available_values = list(_values.values())
