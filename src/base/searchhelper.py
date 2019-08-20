from typing import List, Optional

from src.base.mapping import Mapping


class SearchHelperMixin:
    """
    SearchHelperMixin provides possibility to get mapping and search helpers for user-friendly search API
    """

    fields_to_exclude_from_mapping: Optional[List[str]] = None

    _mapping_class = None

    _full_mapping: Optional[Mapping] = None
    _raw_mapping = None

    @classmethod
    def fill_mapping(cls):
        if cls._full_mapping is None:
            cls._full_mapping = cls._get_mapping()

    @classmethod
    def get_mapping(cls) -> List[str]:
        """
        Returns full mapping with handwritten fields in search set class and their sources
        Except of excluded fields/sources
        """
        cls.fill_mapping()
        return list(cls._full_mapping.keys())

    @classmethod
    def get_fields_values(cls, field_name, prefix='') -> List[str]:
        """
        Returns search helpers for field by prefix
        """
        cls.fill_mapping()
        return cls._full_mapping.get_values(field_name=field_name, prefix=prefix)

    @classmethod
    def get_raw_mapping(cls):
        """
        Caches raw mapping and return it
        """
        if cls._raw_mapping is None:
            cls._raw_mapping = cls._get_raw_mapping()
        return cls._raw_mapping

    @classmethod
    def _get_mapping(cls):
        """
        Returns mapping extended by handwritten fields and its sources
        """

        if cls.fields_to_exclude_from_mapping is not None:
            fields_to_exclude_from_mapping = cls.fields_to_exclude_from_mapping
        else:
            fields_to_exclude_from_mapping = list()

        mapping = cls._mapping_class(cls.Meta.model)

        # create mapping values from fields in searchset class
        for field_name, field in cls.get_field_name_to_field().items():
            if field_name not in fields_to_exclude_from_mapping:
                mapping.add_value(name=field_name, sources=field.sources,
                                  get_available_values_method=field.get_available_values_method)
            if not field.exclude_sources_from_mapping:
                mapping.update_raw_sources(field.sources,
                                           get_available_values_method=field.get_available_values_method)

        # update mapping from mapping in database/elastic/etc
        raw_mapping = cls.get_raw_mapping()
        mapping.update_raw_sources((name for name in raw_mapping if name not in fields_to_exclude_from_mapping))

        return mapping

    @classmethod
    def _get_raw_mapping(cls) -> List[str]:
        """
        That method allows to get mapping in raw format. It have to be reimplemented
        """
        raise NotImplementedError()
