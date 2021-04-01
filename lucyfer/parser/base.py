from lucyparser import parse
from lucyparser.exceptions import BaseLucyException
from lucyparser.tree import BaseNode

from lucyfer.utils import LuceneSearchException


__all__ = [
    'BaseLuceneParserMixin'
]


class BaseLuceneParserMixin:
    @classmethod
    def parse(cls, raw_expression: str):
        """
        Parses raw expression to query tree
        """
        tree = cls._get_tree_from_raw_expression(raw_expression=raw_expression)

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

    @classmethod
    def get_saved_search(cls, tree):
        """
        Add availability to use saved searches. For ex. you can save it in database and get it here.
        """
        return None

    @classmethod
    def _get_tree_from_raw_expression(cls, raw_expression):
        """
        Parses raw search string to lucy tree
        If you want to use some literals except of `string.ascii_letters + string.digits + "-.*_?!;,:@|"`
        you have to:
        1. override lucyparser's Parser class and define your own value_chars in it
        2. override that func and force your Parser class to parse func
        """
        try:
            return parse(string=raw_expression)
        except BaseLucyException:
            raise LuceneSearchException()
