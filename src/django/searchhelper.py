from src.base.searchhelper import SearchHelperMixin


class DjangoSearchHelperMixin(SearchHelperMixin):
    @classmethod
    def _get_raw_mapping(cls):
        return cls.Meta.model._meta.fields
