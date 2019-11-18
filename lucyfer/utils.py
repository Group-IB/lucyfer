class LuceneSearchException(Exception):
    pass


class LuceneSearchCastValueException(LuceneSearchException):
    pass


class LuceneSearchInvalidValueException(LuceneSearchException):
    pass


def fill_field_if_it_necessary(field_name_to_constructor):
    def inner(func):
        def wrapper(*args, **kwargs):
            self_or_cls = args[0]

            for field_name, constructor in field_name_to_constructor.items():
                if getattr(self_or_cls, field_name, None) is None:
                    setattr(self_or_cls, field_name, constructor())

            return func(*args, **kwargs)
        return wrapper
    return inner
