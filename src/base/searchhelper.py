from collections import OrderedDict


# todo db replaces


class MappingValue:
    name = None
    source = None
    _cached_values = None
    _max_cached_values_by_prefix = 10

    def __init__(self, name, sources=None):
        self.name = name
        self.source = sources if sources is not None else [name]

    def get_values(self, prefix=''):
        if self._cached_values is None:
            self._cached_values = dict()
        elif prefix in self._cached_values:
            return self._cached_values[prefix]
        self._cached_values[prefix] = self._get_values(prefix)

    def _get_values(self, prefix):
        raise NotImplementedError()


class Mapping(OrderedDict):
    value_class = None

    def update_raw_sources(self, raw_sources):
        self.update({source: self.value_class(name=source) for source in raw_sources})

    def update_named_sources(self, name_to_sources):
        self.update({name: self.value_class(name=name, sources=source) for name, source in name_to_sources.items()})


class SearchHelperMixin:
    """
    SearchHelperMixin provides possibility to get mapping and search helpers for user-friendly search API
    """

    fields_to_exclude_from_mapping = None

    _full_mapping = None
    _raw_mapping = None

    @classmethod
    def get_mapping(cls):
        """
        Returns full mapping with handwritten fields in search set class and their sources
        Except of excluded fields/sources
        """
        if cls._full_mapping is None:
            cls._full_mapping = cls._get_mapping()
        return cls._full_mapping.keys()

    @classmethod
    def get_fields_values(cls, field_name, prefix=''):
        if field_name not in cls.get_mapping():
            return []

        return cls._full_mapping[field_name].get_values(prefix=prefix)

    @classmethod
    def get_raw_mapping(cls):
        """
        Caches raw mapping and return it
        """
        if cls._raw_mapping is None:
            cls._raw_mapping = cls._get_raw_mapping()
        return cls._raw_mapping

    @classmethod
    def _get_mapping(cls) -> Mapping:
        """
        Returns mapping extended by handwritten fields and its sources
        """

        if cls.fields_to_exclude_from_mapping is not None:
            fields_to_exclude_from_mapping = cls.fields_to_exclude_from_mapping
        else:
            fields_to_exclude_from_mapping = list()

        mapping = Mapping()

        # create mapping values from fields in searchset class
        for field_name, field in cls.get_field_name_to_field().items():
            if field_name not in fields_to_exclude_from_mapping:
                mapping[field_name] = Mapping.value_class(name=field_name, sources=field.sources)
            if not field.exclude_sources_from_mapping:
                mapping.update_raw_sources(field.sources)

        # update mapping from mapping in database/elastic/etc
        raw_mapping = cls.get_raw_mapping()
        mapping.update_raw_sources((name for name in raw_mapping if name not in fields_to_exclude_from_mapping))

        return mapping

    @classmethod
    def _get_raw_mapping(cls) -> list:
        """
        That method allows to get mapping in raw format. It have to be reimplemented
        """
        raise NotImplementedError()
