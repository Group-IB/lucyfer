from django.utils.decorators import classproperty


class SearchHelperMixin:
    fields_to_exclude = []

    _full_fields_to_exclude = None
    _mapping = None

    @classmethod
    def exclude_mapping_fields(cls, mapping):
        return list(set(mapping) - set(cls.full_fields_to_exclude))

    @classproperty
    def full_fields_to_exclude(cls):
        if cls._full_fields_to_exclude is None:
            cls._full_fields_to_exclude = cls.fields_to_exclude

            for name, _cls in cls.field_name_to_field.items():
                if _cls.exclude_sources_from_mapping:
                    cls._full_fields_to_exclude.extend(_cls.get_sources(name))

        return cls._full_fields_to_exclude

    @classmethod
    def get_mapping(cls):
        if cls._mapping is None:
            cls._mapping = cls.exclude_mapping_fields(cls._get_mapping())
        return cls._mapping

    @classmethod
    def _get_mapping(cls):
        raise NotImplementedError()
