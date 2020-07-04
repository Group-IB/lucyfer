from typing import Dict

from lucyfer.parser import LuceneToElasticParserMixin
from lucyfer.searchset.base import BaseSearchSet
from lucyfer.searchset.fields.elastic import default_elastic_field_types_to_fields, ElasticSearchField, \
    ElasticQueryStringField
from lucyfer.searchset.utils import FieldType
from lucyfer.utils import LuceneSearchException


elastic_data_type_to_field_type = {
    "long": FieldType.INTEGER,
    "integer": FieldType.INTEGER,
    "short": FieldType.INTEGER,
    "double": FieldType.FLOAT,
    "float": FieldType.FLOAT,
    "boolean": FieldType.BOOLEAN,
    "date": FieldType.TIMESTAMP,
    "date_nanos": FieldType.TIMESTAMP,
}


class ElasticSearchSet(LuceneToElasticParserMixin, BaseSearchSet):
    _field_base_class = ElasticSearchField
    _default_field = ElasticSearchField
    _field_class_for_default_searching = ElasticQueryStringField

    _field_type_to_field_class = default_elastic_field_types_to_fields
    _raw_type_to_field_type = elastic_data_type_to_field_type

    @classmethod
    def get_es_client(cls, **kwargs):
        raise NotImplementedError()

    @classmethod
    def filter(cls, search, search_terms, raise_exception=False):
        query = cls.parse(raw_expression=search_terms)
        if query is None:
            if raise_exception:
                raise LuceneSearchException()
            else:
                return None

        return search.query(query)

    @classmethod
    def _format_mapping_values(cls, mapping, prefix="") -> Dict[str, FieldType]:
        field_name_to_field_type = dict()

        for key, value in mapping.items():
            if "properties" in value:
                field_name_to_field_type.update(
                    cls._format_mapping_values(value["properties"], ".".join([prefix, key]) if prefix else key)
                )
            else:
                field_name = ".".join([prefix, key]) if prefix else key
                field_name_to_field_type[field_name] = cls._raw_type_to_field_type.get(value.get("type"))

        return field_name_to_field_type

    @classmethod
    def _get_raw_mapping(cls) -> Dict[str, FieldType]:
        model_instance = cls._meta.model()
        index_to_mapping = cls.get_es_client().indices.get_mapping(index=model_instance._get_index())
        if not index_to_mapping:
            return dict()

        last_index = max(index_to_mapping)

        try:
            last_mapping = index_to_mapping[last_index]['mappings'][model_instance._doc_type.name]['properties']
        except KeyError:
            return dict()

        field_name_to_field_type = cls._format_mapping_values(last_mapping)
        return field_name_to_field_type
