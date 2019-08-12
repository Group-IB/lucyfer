from lucyparser.tree import ExpressionNode, AndNode, OrNode, NotNode

from src.base.parser import BaseLuceneParserMixin


class LuceneToElasticParserMixin(BaseLuceneParserMixin):
    @classmethod
    def _parse_tree(cls, tree):
        if isinstance(tree, ExpressionNode):
            return cls.get_query_for_field(tree)

        if isinstance(tree, AndNode):
            query = Q()
            for child in tree.children:
                query = query & cls._parse_tree(tree=child)
            return (query)

        if isinstance(tree, OrNode):
            query = Q()
            for child in tree.children:
                query = query | cls._parse_tree(tree=child)
            return (query)

        if isinstance(tree, NotNode):
            children_query = Q()
            for child in tree.children:
                children_query = children_query & cls._parse_tree(tree=child)
            return ~Q(children_query)

        return Q()
