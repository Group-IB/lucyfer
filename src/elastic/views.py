from ..base.views import MappingMixin


class ElasticMappingMixin(MappingMixin):
    def _get_search_values(self, field_name, prefix):
        try:
            return self.search_class.get_fields_values(qs=self.do_search(),
                                                       field_name=field_name,
                                                       prefix=prefix,
                                                       cache_key=self._get_cache_key())
        except AttributeError:
            return None
