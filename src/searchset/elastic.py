from typing import Dict

from ..searchset.fields.elastic import ElasticSearchField
from ..searchset.mapping import ElasticMapping
from ..searchset.utils import FieldType
from ..parser import LuceneToElasticParserMixin

from .base import BaseSearchSet
from .fields.elastic import default_eclipse_field_types_to_fields


elastic_data_type_to_field_type = {
    "long": FieldType.INTEGER,
    "integer": FieldType.INTEGER,
    "short": FieldType.INTEGER,
    "double": FieldType.FLOAT,
    "float": FieldType.FLOAT,
    "boolean": FieldType.NULL_BOOLEAN,
}


class ElasticSearchSet(LuceneToElasticParserMixin, BaseSearchSet):
    _field_base_class = ElasticSearchField
    _default_field = ElasticSearchField

    _field_type_to_field_class = default_eclipse_field_types_to_fields
    _elastic_data_type_to_field_type = elastic_data_type_to_field_type

    @classmethod
    def filter(cls, search, search_terms):
        query = cls.parse(raw_expression=search_terms)
        return None if query is None else search.query(query)

    # for search helper

    _mapping_class = ElasticMapping

    @classmethod
    def _format_mapping_values(cls, mapping, prefix="") -> Dict[str, FieldType]:
        field_name_to_field_type = dict()

        for key, value in mapping.items():
            if "properties" in value:
                field_name_to_field_type.update(cls._format_mapping_values(value["properties"], ".".join([prefix, key]) if prefix else key))
            else:
                field_name = ".".join([prefix, key]) if prefix else key
                field_name_to_field_type[field_name] = cls._elastic_data_type_to_field_type.get(value.get("type"))

        return field_name_to_field_type

    @classmethod
    def _get_raw_mapping(cls) -> Dict[str, FieldType]:
        model_instance = cls.Meta.model()
        index_to_mapping = cls.Meta.model._get_es_client().indices.get_mapping(index=model_instance._get_index())
        if not index_to_mapping:
            return dict()

        last_index = max(index_to_mapping)

        try:
            last_mapping = index_to_mapping[last_index]['mappings'][model_instance._doc_type.name]['properties']
        except KeyError:
            return dict()

        field_name_to_field_type = cls._format_mapping_values(last_mapping)
        return field_name_to_field_type
