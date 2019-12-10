from lucyparser import parse
from lucyparser.exceptions import BaseLucyException
from lucyparser.tree import BaseNode
from lucyparser.parsing import Parser as LucyParser

from lucyfer.utils import LuceneSearchException


class CyrillicParser(LucyParser):
    # with redefined `permitted_name_value_char` it's only used for error messages
    value_chars = "letter, digit, or one of -.*_?!;,:@|"

    def permitted_name_value_char(self, c: str):
        return c.isalnum() or c in "-.*_?!;,:@|"


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
        try:
            return parse(string=raw_expression, parser_class=CyrillicParser)
        except BaseLucyException:
            raise LuceneSearchException()
