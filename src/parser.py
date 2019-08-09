from django.db.models import Q
from lucyparser import parse
from lucyparser.tree import ExpressionNode, AndNode, OrNode, NotNode

from src.utils import LuceneSearchError


class BaseLuceneParserMixin:
    @classmethod
    def _parse_tree(cls, tree):
        raise NotImplementedError()

    @classmethod
    def parse(cls, raw_expression):

        try:
            tree = parse(string=raw_expression)
        except Exception:
            raise LuceneSearchError()

        return cls._parse_tree(tree=tree)


class LuceneToDjangoParserMixin(BaseLuceneParserMixin):
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
            # TODO ANN
            return Q()

        return Q()
