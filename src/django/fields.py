from django.db.models import Q
from lucyparser.tree import Operator

from src.base.fields import BaseSearchField
from src.utils import LuceneSearchCastValueException


class DjangoSearchField(BaseSearchField):
    def get_query(self, condition):
        if self.match_all(value=condition.value):
            return Q()

        return self.create_query_for_sources(condition=condition)

    def create_query_for_sources(self, condition):
        query = Q()

        lookup = self.get_lookup(condition.operator)
        value = self.cast_value(condition.value)

        for source in self.get_sources(condition.name):
            query = query | Q(**{"{}__{}".format(source, lookup): value})
        return query


class CharField(DjangoSearchField):
    OPERATOR_TO_LOOKUP = {
        Operator.EQ: "icontains",
    }

    def get_query(self, condition):
        if self.match_all(value=condition.value):
            return Q()

        wildcard_parts = self.cast_value(condition.value).split("*")

        parts_count = len(wildcard_parts)

        if parts_count == 1:
            return self.create_query_for_sources(condition)

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


class NumberField(DjangoSearchField):
    OPERATOR_TO_LOOKUP = {
        Operator.GTE: "gte",
        Operator.LTE: "lte",
        Operator.GT: "gt",
        Operator.LT: "lt",
        Operator.EQ: "exact",
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


class BooleanField(DjangoSearchField):
    OPERATOR_TO_LOOKUP = {
        Operator.EQ: "exact",
    }

    _values = {"true": True, "false": False}

    def cast_value(self, value):
        value = value.lower()
        if value in self._values:
            return self._values[value]

        raise LuceneSearchCastValueException()


class NullBooleanField(BooleanField):
    _values = {"true": True, "false": False, "null": None}
