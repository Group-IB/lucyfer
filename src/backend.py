from rest_framework.compat import distinct
from rest_framework.filters import SearchFilter

from src.utils import LuceneSearchError


class LuceneSearchFilter(SearchFilter):
    def get_searchset_class(self, view, request):
        """
        Returns searchset class if it presented in view
        """
        return getattr(view, 'search_class', None)

    def get_base_search_terms(self, request):
        """
        Search terms are set by a ?search=... query parameter,
        and may be comma and/or whitespace delimited.
        """
        return request.query_params.get(self.search_param, '')

    def lucene_filter_queyset(self, searchset_class, search_terms, queryset):
        if searchset_class is not None:
            try:
                query = searchset_class.parse(raw_expression=search_terms)
                return queryset.filter(query)
            except LuceneSearchError:
                return None
        return None

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
            if self.must_call_distinct(queryset, searchset_class.field_sources):
                queryset = distinct(filtered_queryset, queryset)
            else:
                queryset = filtered_queryset

        return queryset
