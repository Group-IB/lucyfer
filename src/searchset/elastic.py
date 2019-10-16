from ..searchset.fields.elastic import ElasticSearchField
from ..searchset.mapping import ElasticMapping
from ..parser import LuceneToElasticParserMixin

from .base import BaseSearchSet
from .fields.elastic import default_eclipse_field_types_to_fields


class ElasticSearchSet(LuceneToElasticParserMixin, BaseSearchSet):
    _field_base_class = ElasticSearchField
    _default_field = ElasticSearchField
    _field_type_to_field_class = default_eclipse_field_types_to_fields

    @classmethod
    def filter(cls, search, search_terms):
        query = cls.parse(raw_expression=search_terms)
        return None if query is None else search.query(query)

    # for search helper

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
