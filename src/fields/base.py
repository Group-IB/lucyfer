class BaseSearchField:
    def __init__(self, source=None, *args, **kwargs):
        self.source = source

    def get_source(self, field_name):
        return self.source or field_name

    def get_query(self, field_name, lookup, value):
        raise NotImplementedError()
