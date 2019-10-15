from lucyparser import parse
from lucyparser.exceptions import BaseLucyException
from lucyparser.tree import BaseNode

from ..utils import LuceneSearchException


class BaseLuceneParserMixin:
    @classmethod
    def parse(cls, raw_expression: str):
        """
        Parses raw expression to query tree
        """

        try:
            tree = parse(string=raw_expression)
        except BaseLucyException:
            raise LuceneSearchException()

        parsed_tree = cls._parse_tree(tree=tree)

        if parsed_tree is None:
            raise LuceneSearchException()

        return parsed_tree

    @classmethod
    def _parse_tree(cls, tree: BaseNode):
        """
        Parses lucyparsers tree to query tree
        """
        raise NotImplementedError()
