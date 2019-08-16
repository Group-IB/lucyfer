from collections import defaultdict


# todo cache
# todo db replaces
# todo check if field is source or just field name


class MappingValue:
    name = None
    source = None
    _cached_values = None

    def __init__(self, name, source=None):
        self.name = name
        self.source = source if source is not None else name


class Mapping(dict):
    def update_raw_sources(self, raw_sources):
        self.update({source: MappingValue(name=source) for source in raw_sources})

    def update_named_sources(self, name_to_sources):
        self.update({name: MappingValue(name=name, source=source) for name, source in name_to_sources.items()})


class SearchHelperMixin:
    """
    SearchHelperMixin provides possibility to get mapping and search helpers for user-friendly search API
    """

    fields_to_exclude_from_mapping = None

    _full_mapping = None
    _raw_mapping = None
    _cached_field_values = None

    @classmethod
    def exclude_mapping_fields(cls, mapping):
        """
        Returns mapping without fields to exclude
        it may be:
            1) sources inside of fields
            2) fields in cls.fields_to_exclude_from_mapping
        """

        if cls.fields_to_exclude_from_mapping is not None:
            fields_to_exclude_from_mapping = cls.fields_to_exclude_from_mapping
        else:
            fields_to_exclude_from_mapping = list()

        for field in cls.get_field_name_to_field().values():
            if field.exclude_sources_from_mapping:
                fields_to_exclude_from_mapping.extend(field.sources)

        return list(set(mapping) - set(fields_to_exclude_from_mapping))

    # @classmethod
    # def get_cached_field_values(cls):
    #     if cls._cached_field_values is None:
    #         cls._cached_field_values = cls._get_cached_field_values()
    #     return cls._cached_field_values

    @classmethod
    def get_mapping(cls):
        """
        Returns full mapping with handwritten fields in search set class and their sources
        Except of excluded fields/sources
        """
        if cls._full_mapping is None:
            cls._full_mapping = sorted(cls.exclude_mapping_fields(cls._get_mapping()))
        return cls._full_mapping

    @classmethod
    def get_fields_values(cls, field_name, prefix=''):
        if field_name not in cls.get_mapping():
            return []
        # TODO
        return []

    @classmethod
    def get_raw_mapping(cls):
        """
        Caches raw mapping and return it
        """
        if cls._raw_mapping is None:
            cls._raw_mapping = cls._get_raw_mapping()
        return cls._raw_mapping

    # @classmethod
    # def _get_cached_field_values(cls):
    #     field_to_values = defaultdict(list)
    #

    @classmethod
    def _get_mapping(cls):
        """
        Returns mapping extended by handwritten fields and its sources
        """
        all_sources = []

        for field_name, field in cls.get_field_name_to_field().items():
            all_sources.append(field_name)
            all_sources.extend(field.sources)

        all_sources.extend(cls.get_raw_mapping())

        return list(set(all_sources))

    @classmethod
    def _get_raw_mapping(cls):
        """
        That method allows to get mapping in raw format. It have to be reimplemented
        """
        raise NotImplementedError()
