EXPRESSION_OPERATOR_TO_LOOKUP = {">=": "gte",
                                 "<=": "lte",
                                 "<": "lt",
                                 ">": "gt",
                                 ":": "iexact"}


class LuceneSearchError(Exception):
    pass


class LuceneSearchCastValueError(LuceneSearchError):
    pass
