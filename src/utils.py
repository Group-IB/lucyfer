class LuceneSearchException(Exception):
    pass


class LuceneSearchCastValueException(LuceneSearchException):
    pass


class LuceneSearchInvalidValueException(LuceneSearchException):
    pass


class classproperty:
    def __init__(self, method=None):
        self.fget = method

    def __get__(self, instance, cls=None):
        return self.fget(cls)

    def getter(self, method):
        self.fget = method
        return self
