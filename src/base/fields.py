from lucyparser.tree import Operator


class BaseSearchField:
    OPERATOR_TO_LOOKUP = dict()
    DEFAULT_LOOKUP = None

    def __init__(self, source=None, sources=None, *args, **kwargs):
        sources = list() if sources is None else sources

        if source is not None:
            sources.append(source)

        self.sources = set(sources)

    def cast_value(self, value):
        return value

    def get_lookup(self, operator):
        return self.OPERATOR_TO_LOOKUP.get(operator, self.DEFAULT_LOOKUP)

    def get_sources(self, field_name):
        return self.sources or [field_name]

    def get_query(self, condition):
        raise NotImplementedError()

    def match_all(self, value):
        return value == "*"


def negate_query_if_necessary(func):
    def wrapper(self, condition):
        query = func(self, condition)
        if condition.operator == Operator.NEQ:
            query = query.__invert__()
        return query
    return wrapper
