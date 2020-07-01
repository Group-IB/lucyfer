from collections import defaultdict
from typing import List


from elasticsearch.exceptions import RequestError
from lucyfer.searchset.fields.mapping.base import MappingMixin


class ElasticMappingMixin(MappingMixin):
    def prepare_qs_for_suggestions(self, qs, prefix: str):
        search = qs.extra(size=0).query('query_string', **{"fields": self.sources, "query": f'*{prefix}*'})
        for source in self.sources:
            search.aggs.bucket(source, "terms", field=source)
        return search

    def get_suggestions_from_prepared_qs(self, qs, prefix: str) -> List[str]:
        try:
            aggs = qs.execute().to_dict().get("aggregations", defaultdict(dict))
        except RequestError:
            return []
        result = []
        for source in self.sources:
            if aggs[source].get("buckets"):
                result.extend(
                    [val for val
                     in [str(val["key"]) for val in aggs[source]["buckets"]]
                     if prefix in val]
                )
        return list(set(result))
