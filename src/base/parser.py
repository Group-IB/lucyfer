from lucyparser import parse
from lucyparser.exceptions import BaseLucyException

from src.utils import LuceneSearchException


class BaseLuceneParserMixin:
    @classmethod
    def _parse_tree(cls, tree):
        raise NotImplementedError()

    @classmethod
    def parse(cls, raw_expression):

        try:
            tree = parse(string=raw_expression)
        except BaseLucyException:
            raise LuceneSearchException()

        return cls._parse_tree(tree=tree)
