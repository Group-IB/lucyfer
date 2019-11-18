from django.db.models import Q
from lucyparser.tree import ExpressionNode, AndNode, OrNode, NotNode

from lucyfer.parser.base import BaseLuceneParserMixin
from lucyfer.settings import lucyfer_settings


class LuceneToDjangoParserMixin(BaseLuceneParserMixin):
    @classmethod
    def _parse_tree(cls, tree):
        if isinstance(tree, ExpressionNode):
            if lucyfer_settings.SAVED_SEARCHES_ENABLE and tree.name == lucyfer_settings.SAVED_SEARCHES_KEY:
                return cls.get_saved_search(tree)

            return cls.get_query_for_field(tree)

        is_and_node = isinstance(tree, AndNode)
        is_or_node = isinstance(tree, OrNode)
        is_not_node = isinstance(tree, NotNode)

        query = Q()

        if is_and_node or is_not_node or is_or_node:
            queries = [cls._parse_tree(tree=child) for child in tree.children]
            queries = [q for q in queries if q is not None]

            if is_and_node:
                for q in queries:
                    query = query & q
                query = (query)

            elif is_or_node:
                for q in queries:
                    query = query | q
                query = (query)

            elif is_not_node:
                for q in queries:
                    query = query & q
                query = ~Q(query)

        return query
