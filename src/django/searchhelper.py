from src.base.searchhelper import SearchHelperMixin


class DjangoSearchHelperMixin(SearchHelperMixin):
    @classmethod
    def _get_raw_mapping(cls):
        # TODO
        return []
