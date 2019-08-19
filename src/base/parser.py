from lucyparser import parse
from lucyparser.exceptions import BaseLucyException
from lucyparser.tree import BaseNode

from src.utils import LuceneSearchException


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

        return cls._parse_tree(tree=tree)

    @classmethod
    def _parse_tree(cls, tree: BaseNode):
        """
        Parses lucyparsers tree to query tree
        """
        raise NotImplementedError()
