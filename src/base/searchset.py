from src.utils import classproperty


class BaseSearchSet:
    _field_name_to_search_field_instance = None
    _field_sources = None
    _field_base_class = None

    @classproperty
    def field_name_to_field(cls):
        if cls._field_name_to_search_field_instance is None:
            cls._field_name_to_search_field_instance = {name: _cls
                                                        for name, _cls in cls.__dict__.items()
                                                        if isinstance(_cls, cls._field_base_class)}

        return cls._field_name_to_search_field_instance

    @classproperty
    def field_sources(cls):
        if cls._field_sources is None:
            cls._field_sources = []

            for name, _cls in cls.field_name_to_field.items():
                cls._field_sources.extend(_cls.get_sources(name))

        return cls._field_sources

    @classmethod
    def get_query_for_field(cls, condition):
        return cls.field_name_to_field.get(condition.name, cls._field_base_class()).get_query(condition)
