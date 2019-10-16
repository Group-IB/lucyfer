from elasticsearch_dsl import Q
from elasticsearch_dsl.query import Range
from lucyparser.tree import Operator

from ...searchset.utils import FieldType
from ...utils import LuceneSearchCastValueException

from .base import BaseSearchField, negate_query_if_necessary


class ElasticSearchField(BaseSearchField):
    DEFAULT_LOOKUP = "term"

    OPERATOR_TO_LOOKUP = {
        Operator.EQ: DEFAULT_LOOKUP,
        Operator.NEQ: DEFAULT_LOOKUP,
        Operator.GT: "gt",
        Operator.LT: "lt",
        Operator.GTE: "gte",
        Operator.LTE: "lte"
    }

    def create_query_for_sources(self, condition):
        lookup = self.get_lookup(condition.operator)
        value = self.cast_value(condition.value)
        sources = self.get_sources(condition.name)

        if lookup == self.DEFAULT_LOOKUP:
            return self._get_query_for_term(sources=sources, lookup=lookup, value=value)
        else:
            return self._get_query_for_range(sources=sources, lookup=lookup, value=value)

    def _get_query_for_term(self, sources, lookup, value):
        query = None  # if set Q() as default it will be MatchAll() anytime

        lookup = self._get_wildcard_or_lookup(value=value, lookup=lookup)

        for source in sources:
            if query is None:
                query = Q(lookup, **{source: value})
            else:
                query = query | Q(lookup, **{source: value})
        return query

    def _get_query_for_range(self, sources, lookup, value):
        query = None  # if set Q() as default it will be MatchAll() anytime
        for source in sources:
            if query is None:
                query = Range(**{source: {lookup: value}})
            else:
                query = query | Range(**{source: {lookup: value}})
        return query

    def _get_wildcard_or_lookup(self, value, lookup):
        return "wildcard" if "*" in value else lookup

    @negate_query_if_necessary
    def get_query(self, condition):
        if self.match_all(value=condition.value):
            return None

        return self.create_query_for_sources(condition=condition)


class ElasticSearchFieldWithoutWildCard(ElasticSearchField):
    def _get_wildcard_or_lookup(self, value, lookup):
        return lookup


class ElasticIntegerField(ElasticSearchFieldWithoutWildCard):
    def cast_value(self, value):
        try:
            return int(value)
        except (ValueError, TypeError):
            raise LuceneSearchCastValueException()


class ElasticFloatField(ElasticSearchFieldWithoutWildCard):
    def cast_value(self, value):
        try:
            return float(value)
        except (ValueError, TypeError):
            raise LuceneSearchCastValueException()


class ElasticBooleanField(ElasticSearchFieldWithoutWildCard):
    DEFAULT_LOOKUP = "match"

    OPERATOR_TO_LOOKUP = {
        Operator.EQ: "match",
        Operator.NEQ: "match",
    }

    _values = {"true": True, "false": False}
    _default_get_available_values_method = _values.keys

    def create_query_for_sources(self, condition):
        lookup = self.get_lookup(condition.operator)
        value = self.cast_value(condition.value)
        sources = self.get_sources(condition.name)

        if lookup == self.DEFAULT_LOOKUP:
            return self._get_query_for_term(sources=sources, lookup=lookup, value=value)
        return None

    def cast_value(self, value):
        value = value.lower()
        if value in self._values:
            return self._values[value]

        raise LuceneSearchCastValueException()


class ElasticNullBooleanField(ElasticBooleanField):
    _values = {"true": True, "false": False, "null": None}
    _default_get_available_values_method = _values.keys


default_eclipse_field_types_to_fields = {
    FieldType.BOOLEAN: ElasticBooleanField,
    FieldType.INTEGER: ElasticIntegerField,
    FieldType.NULL_BOOLEAN: ElasticNullBooleanField,
    FieldType.FLOAT: ElasticFloatField,
}
