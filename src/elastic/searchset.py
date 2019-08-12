from src.base.searchset import BaseSearchSet
from src.elastic.parser import LuceneToElasticParserMixin


class ElasticSearchSet(LuceneToElasticParserMixin, BaseSearchSet):
    _field_base_class = None

    @classmethod
    def filter(cls, search, search_terms):
        query = cls.parse(raw_expression=search_terms)
        return search.query(query)
