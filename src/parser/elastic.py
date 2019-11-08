from elasticsearch_dsl import Q
from lucyparser.tree import ExpressionNode, AndNode, OrNode, NotNode

from .base import BaseLuceneParserMixin


class LuceneToElasticParserMixin(BaseLuceneParserMixin):
    @classmethod
    def _parse_tree(cls, tree):
        if isinstance(tree, ExpressionNode):
            return cls.get_query_for_field(tree) or ~Q()

        query = ~Q()

        is_and_node = isinstance(tree, AndNode)
        is_or_node = isinstance(tree, OrNode)
        is_not_node = isinstance(tree, NotNode)

        if is_and_node or is_not_node or is_or_node:
            queries = [cls._parse_tree(tree=child) for child in tree.children]

            query = queries[0]

            if is_and_node:
                for q in queries[1:]:
                    query = query & q

            elif is_or_node:
                for q in queries[1:]:
                    query = query | q

            elif is_not_node:
                for q in queries[1:]:
                    query = query & q
                query = ~Q(query)

        return query
