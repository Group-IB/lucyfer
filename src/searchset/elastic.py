from .base import BaseSearchSet
from ..searchset.fields.elastic import ElasticSearchField
from ..parser import LuceneToElasticParserMixin


class ElasticSearchSet(LuceneToElasticParserMixin, BaseSearchSet):
    _field_base_class = ElasticSearchField
    _default_field = ElasticSearchField

    @classmethod
    def filter(cls, search, search_terms):
        query = cls.parse(raw_expression=search_terms)
        return None if query is None else search.query(query)
