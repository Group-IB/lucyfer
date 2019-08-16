from src.base.mapping import MappingValue, Mapping


class ElasticMappingValue(MappingValue):
    def _get_values(self, model, prefix):
        search = model.search().extra(size=0).query('query_string',
                                                    **{"default_field": self.name, "query": f'*{prefix}*'})
        search.aggs.bucket(self.name, "terms", field=self.name)
        result = search.execute().to_dict()["aggregations"][self.name]["buckets"]
        return list(set([str(val["key"]) for val in result if prefix in val["key"]]))


class ElasticMapping(Mapping):
    _value_class = ElasticMappingValue
