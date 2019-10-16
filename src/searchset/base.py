from typing import List, Optional, Dict

from ..searchset.mapping import Mapping
from ..searchset.utils import FieldType
from ..utils import fill_field_if_it_necessary


# todo merge those classes

class SearchHelper:
    """
    SearchHelperMixin provides possibility to get mapping and search helpers for user-friendly search API
    """

    fields_to_exclude_from_mapping: Optional[List[str]] = None
    fields_to_exclude_from_suggestions: Optional[List[str]] = None
    show_suggestions = True
    escape_quotes_in_suggestions = True

    _mapping_class = None

    _full_mapping: Optional[Mapping] = None
    _raw_mapping = None

    @classmethod
    def get_mapping(cls) -> List[str]:
        """
        Returns full mapping with handwritten fields in search set class and their sources
        Except of excluded fields/sources
        """
        return list(cls.get_full_mapping().keys())

    @classmethod
    def get_mapping_to_suggestion(cls) -> Dict[str, bool]:
        return {k: v.show_suggestions for k, v in cls.get_full_mapping().items()}

    @classmethod
    def get_fields_values(cls, qs, field_name, prefix='', cache_key=None) -> List[str]:
        """
        Returns search helpers for field by prefix
        """
        return cls.get_full_mapping().get_values(qs=qs, field_name=field_name, prefix=prefix, cache_key=cache_key)

    @classmethod
    def get_fields_to_exclude_from_mapping(cls) -> List[str]:
        return cls.fields_to_exclude_from_mapping if cls.fields_to_exclude_from_mapping is not None else list()

    @classmethod
    def get_fields_to_exclude_from_suggestions(cls) -> List[str]:
        return cls.fields_to_exclude_from_suggestions if cls.fields_to_exclude_from_suggestions is not None else list()

    @classmethod
    def get_raw_mapping(cls) -> Dict[str, FieldType]:
        """
        Caches raw mapping and return it
        """
        if cls._raw_mapping is None:
            cls._raw_mapping = cls._get_raw_mapping()
        return cls._raw_mapping

    @classmethod
    def get_full_mapping(cls):
        if cls._full_mapping is None:
            cls._fill_mapping()
        return cls._full_mapping

    @classmethod
    def _fill_mapping(cls):
        """
        Fill mapping extended by handwritten fields and its sources
        """

        mapping_exclude = cls.get_fields_to_exclude_from_mapping()
        suggestions_exclude = cls.get_fields_to_exclude_from_suggestions()

        mapping = cls._mapping_class(cls.Meta.model)

        # create mapping values from fields in searchset class
        for field_name, field in cls.get_field_name_to_field().items():

            get_available_values_method = field.get_available_values_method()

            if field_name not in mapping_exclude:
                mapping.add_value(name=field_name,
                                  sources=field.sources,
                                  show_suggestions=(cls.show_suggestions and field.show_suggestions
                                                    and field_name not in suggestions_exclude),
                                  get_available_values_method=get_available_values_method,
                                  escape_quotes_in_suggestions=cls.escape_quotes_in_suggestions)

            if not field.exclude_sources_from_mapping:
                for source in field.sources:
                    mapping.add_value(name=source,
                                      show_suggestions=cls.show_suggestions and source not in suggestions_exclude,
                                      get_available_values_method=get_available_values_method,
                                      escape_quotes_in_suggestions=cls.escape_quotes_in_suggestions)

        # update mapping from mapping in database/elastic/etc
        raw_mapping = cls.get_raw_mapping()

        for name, field_type in raw_mapping.items():
            if name not in mapping_exclude:
                mapping.add_value(name=name,
                                  field_type=field_type,
                                  show_suggestions=cls.show_suggestions and name not in suggestions_exclude,
                                  escape_quotes_in_suggestions=cls.escape_quotes_in_suggestions)
            elif field_type in cls._field_type_to_field_class:
                cls.append_field_source_to_search_field_instance(source=name, instance=cls._field_type_to_field_class[field_type]())

        cls._full_mapping = mapping

    @classmethod
    def _get_raw_mapping(cls) -> Dict[str, FieldType]:
        """
        That method allows to get mapping in raw format. It have to be reimplemented
        """
        raise NotImplementedError()


class BaseSearchSet(SearchHelper):
    _field_base_class = None

    _field_name_to_search_field_instance: Optional[Dict[str, _field_base_class]] = None
    _field_source_to_search_field_instance: Optional[Dict[str, _field_base_class]] = None

    # default field uses for creating query for fields not defined in searchset class
    _default_field = None

    # provides possibility to use auto cast for boolean/integer/etc fields by field classes usage
    # that means we analyze elastic mapping data types or django models to match it to field classes
    _field_type_to_field_class: Optional[Dict[str, _field_base_class]] = None

    @classmethod
    def get_field_name_to_field(cls):
        """
        Returns dictionary with fieldnames defined in searchset class and field instances
        """
        if cls._field_name_to_search_field_instance is None:
            cls._field_name_to_search_field_instance = dict()
            cls._field_source_to_search_field_instance = dict()

            for name, _cls in cls.__dict__.items():
                if isinstance(_cls, cls._field_base_class):

                    cls._field_name_to_search_field_instance[name] = _cls

                    if _cls.sources:
                        for field_source in _cls.sources:
                            cls.append_field_source_to_search_field_instance(source=field_source, instance=_cls.__class__())

        return cls._field_name_to_search_field_instance

    @classmethod
    @fill_field_if_it_necessary({"_field_source_to_search_field_instance": dict})
    def append_field_source_to_search_field_instance(cls, source, instance):
        cls._field_source_to_search_field_instance[source] = instance

    @classmethod
    def get_query_for_field(cls, condition):
        """
        Returns Q object with query for parsed condition
        """

        field = cls.get_field_name_to_field().get(condition.name)

        # if field not presented in hardcoded fields in searchset class maybe it presented in some field sources
        if field is None:
            field = cls._field_source_to_search_field_instance.get(condition.name)

        # if fields is not source we can try to get field instance by field type from mapping
        if field is None:

            # check field type
            field_type = getattr(cls.get_full_mapping().get(condition.name), "field_type", None)

            field = cls._field_type_to_field_class.get(field_type, cls._default_field)()

        # and finally create a query
        return field.get_query(condition)
