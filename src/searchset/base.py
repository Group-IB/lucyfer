from typing import List, Optional


class BaseSearchSet:
    _field_base_class = None
    _field_name_to_search_field_instance = None
    _field_sources: Optional[List[str]] = None
    _default_field = None

    @classmethod
    def get_field_name_to_field(cls):
        """
        Returns dictionary with fieldnames defined in searchset class and field instances
        """
        if cls._field_name_to_search_field_instance is None:
            cls._field_name_to_search_field_instance = {name: _cls
                                                        for name, _cls in cls.__dict__.items()
                                                        if isinstance(_cls, cls._field_base_class)}

        return cls._field_name_to_search_field_instance

    @classmethod
    def get_fields_sources(cls) -> List[str]:
        """
        Returns sources for field defined in searchset class
        """
        if cls._field_sources is None:
            cls._field_sources = list()

            for name, _cls in cls.get_field_name_to_field().items():
                cls._field_sources.extend(_cls.get_sources(name))

        return cls._field_sources

    @classmethod
    def get_query_for_field(cls, condition):
        """
        Returns Q object with query for parsed condition
        """
        return cls.get_field_name_to_field().get(condition.name, cls._default_field()).get_query(condition)
