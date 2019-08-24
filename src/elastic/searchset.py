from ..base.searchset import BaseSearchSet
from ..elastic.fields import ElasticSearchField
from ..elastic.parser import LuceneToElasticParserMixin


class ElasticSearchSet(LuceneToElasticParserMixin, BaseSearchSet):
    _field_base_class = ElasticSearchField

    @classmethod
    def filter(cls, search, search_terms):
        query = cls.parse(raw_expression=search_terms)
        return search.query(query)
