from .base import SearchHelperMixin
from ...searchset.mapping import ElasticMapping


class ElasticSearchHelperMixin(SearchHelperMixin):
    _mapping_class = ElasticMapping

    @classmethod
    def _format_mapping_values(cls, mapping, prefix="") -> list:
        keys = []

        for key, value in mapping.items():
            keys.append(prefix + key)
            if "properties" in value:
                keys.extend(cls._format_mapping_values(value["properties"], "".join([prefix, key, "."])))

        return keys

    @classmethod
    def _get_raw_mapping(cls) -> list:
        model_instance = cls.Meta.model()
        mapping = cls.Meta.model._get_es_client().indices.get_mapping(index=model_instance._get_index())
        if not mapping:
            return []
        last_index = max(mapping.keys())

        try:
            mapping = mapping[last_index]['mappings'][model_instance._doc_type.name]['properties']
        except KeyError:
            return []

        keys = cls._format_mapping_values(mapping)
        return keys
