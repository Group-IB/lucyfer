from elasticsearch_dsl import Q
from lucyparser.tree import Operator

from src.base.fields import BaseSearchField


class ElasticSearchField(BaseSearchField):
    OPERATOR_TO_LOOKUP = {
        Operator.EQ: "terms"
    }

    def get_query(self, condition):
        if self.match_all(value=condition.value):
            return Q()

        return self.create_query_for_sources(condition=condition)

    def create_query_for_sources(self, condition):
        query = Q()

        lookup = self.get_lookup(condition.operator)
        value = self.cast_value(condition.value)

        for source in self.get_sources(condition.name):
            query = query | Q(lookup, **{source: value})

        return query
