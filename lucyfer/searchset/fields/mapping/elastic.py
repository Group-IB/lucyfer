from collections import defaultdict
from typing import List

from lucyfer.searchset.fields.mapping.base import MappingMixin


class ElasticMappingMixin(MappingMixin):
    def _get_values(self, qs, prefix: str) -> List[str]:
        search = qs.extra(size=0).query('query_string', **{"fields": self.sources, "query": f'*{prefix}*'})
        for source in self.sources:
            search.aggs.bucket(source, "terms", field=source)

        aggs = search.execute().to_dict().get("aggregations", defaultdict(dict))
        result = []
        for source in self.sources:
            if aggs[source].get("buckets"):
                result.extend(
                    [val for val
                     in [str(val["key"]) for val in aggs[source]["buckets"]]
                     if prefix in val]
                )

        return list(set(result))
