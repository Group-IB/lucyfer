class BaseSearchField:
    def __init__(self, source=None, sources=None, *args, **kwargs):
        sources = list() if sources is None else sources
        if source is not None:
            sources.append(source)

        self.sources = set(sources)

    def get_sources(self, field_name):
        return self.sources or [field_name]

    def get_query_by_condition(self, condition):
        raise NotImplementedError()
