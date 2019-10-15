from rest_framework.compat import distinct
from rest_framework.filters import SearchFilter

from ..utils import LuceneSearchException


class DjangoLuceneSearchFilterMixin(SearchFilter):
    def filter_queryset(self, request, queryset, view):
        search_terms = self.get_base_search_terms(request)

        # if there nothing to search - return
        if not search_terms:
            return queryset

        # first try to search in lucene way
        searchset_class = self.get_searchset_class(view, request)
        filtered_queryset = self.lucene_filter_queyset(searchset_class=searchset_class, search_terms=search_terms,
                                                       queryset=queryset)

        # if there is nothing to present
        # we give a second chance to common search
        if filtered_queryset is None:
            queryset = super().filter_queryset(request=request, queryset=queryset, view=view)
        else:
            if self.must_call_distinct(queryset, searchset_class.get_fields_sources()):
                queryset = distinct(filtered_queryset, queryset)
            else:
                queryset = filtered_queryset

        return queryset

    def lucene_filter_queyset(self, searchset_class, search_terms, queryset):
        if searchset_class is not None:
            try:
                return searchset_class.filter(queryset, search_terms)
            except LuceneSearchException:
                return None
        return None
