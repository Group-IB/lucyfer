class MappingMixin:
    def _get_cache_key(self):
        """
        Method to get some string as unique id for values caching. It may me username or email for ex.
        """
        return None

    def _get_search_values(self, field_name, prefix):
        raise NotImplementedError()

    def _get_mapping(self):
        try:
            return self.search_class.get_mapping()
        except AttributeError:
            return None
