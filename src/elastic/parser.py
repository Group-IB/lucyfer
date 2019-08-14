from elasticsearch_dsl import Q
from lucyparser.tree import ExpressionNode, AndNode, OrNode, NotNode

from src.base.parser import BaseLuceneParserMixin


class LuceneToElasticParserMixin(BaseLuceneParserMixin):
    @classmethod
    def _parse_tree(cls, tree):
        if isinstance(tree, ExpressionNode):
            return cls.get_query_for_field(tree)

        query = None

        if isinstance(tree, AndNode):
            for child in tree.children:
                if query is None:
                    query = cls._parse_tree(tree=child)
                else:
                    query = query & cls._parse_tree(tree=child)

        elif isinstance(tree, OrNode):
            for child in tree.children:
                if query is None:
                    query = cls._parse_tree(tree=child)
                else:
                    query = query | cls._parse_tree(tree=child)

        elif isinstance(tree, NotNode):
            for child in tree.children:
                if query is None:
                    query = cls._parse_tree(tree=child)
                else:
                    query = query & cls._parse_tree(tree=child)

            if query is not None:
                query = ~Q(query)

        return query if query is not None else Q()
