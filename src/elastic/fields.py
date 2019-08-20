from elasticsearch_dsl import Q
from lucyparser.tree import Operator

from src.base.fields import BaseSearchField, negate_query_if_necessary
from src.utils import LuceneSearchCastValueException


class ElasticSearchField(BaseSearchField):
    DEFAULT_LOOKUP = "term"

    OPERATOR_TO_LOOKUP = {
        Operator.EQ: "term",
        Operator.NEQ: "term",
    }

    def create_query_for_sources(self, condition):
        query = None  # if set Q() as default it will be MatchAll() anytime

        lookup = self.get_lookup(condition.operator)
        value = self.cast_value(condition.value)

        for source in self.get_sources(condition.name):
            if query is None:
                query = Q(lookup, **{source: value})
            else:
                query = query | Q(lookup, **{source: value})
        return query

    @negate_query_if_necessary
    def get_query(self, condition):
        if self.match_all(value=condition.value):
            return None

        return self.create_query_for_sources(condition=condition)


class RangeOrMatchField(ElasticSearchField):
    OPERATOR_TO_LOOKUP = {
        Operator.EQ: "match",
        Operator.NEQ: "match",
        Operator.GT: "gt",
        Operator.LT: "lt",
        Operator.GTE: "gte",
        Operator.LTE: "lte"
    }

    def create_query_for_sources(self, condition):
        if condition.operator in [Operator.EQ, Operator.NEQ]:
            return super().create_query_for_sources(condition)

        lookup = self.get_lookup(condition.operator)
        value = self.cast_value(condition.value)

        query = None  # if set Q() as default it will be MatchAll() anytime

        for source in self.get_sources(condition.name):
            if query is None:
                query = Q("range", **{source: {lookup: value}})
            else:
                query = query | Q("range", **{source: {lookup: value}})

        return query


class IntegerField(RangeOrMatchField):
    def cast_value(self, value):
        try:
            return int(value)
        except (ValueError, TypeError):
            raise LuceneSearchCastValueException()


class FloatField(RangeOrMatchField):
    def cast_value(self, value):
        try:
            return float(value)
        except (ValueError, TypeError):
            raise LuceneSearchCastValueException()


class BooleanField(ElasticSearchField):
    OPERATOR_TO_LOOKUP = {
        Operator.EQ: "match",
        Operator.NEQ: "match",
    }

    _values = {"true": True, "false": False}

    def cast_value(self, value):
        value = value.lower()
        if value in self._values:
            return self._values[value]

        raise LuceneSearchCastValueException()


class NullBooleanField(BooleanField):
    _values = {"true": True, "false": False, "null": None}
