from django.utils.decorators import classproperty

from src.fields import DjangoSearchField
from src.parser import LuceneToDjangoParserMixin
from src.utils import LuceneSearchError, EXPRESSION_OPERATOR_TO_LOOKUP


class BaseSearchSet:
    _field_name_to_search_field_instance = None
    _field_sources = None

    @classproperty
    def field_name_to_field(cls):
        if cls._field_name_to_search_field_instance is None:
            cls._field_name_to_search_field_instance = {name: _cls
                                                        for name, _cls in cls.__dict__.items()
                                                        if isinstance(_cls, DjangoSearchField)}

        return cls._field_name_to_search_field_instance

    @classproperty
    def field_sources(cls):
        if cls._field_sources is None:
            cls._field_sources = [_cls.get_source(name) for name, _cls in cls.field_name_to_field.items()]
        return cls._field_sources

    @classmethod
    def validate_tokens(cls, variable_name_to_raw_value):
        variable_name_to_query_term = dict()

        for variable_name, raw_value in variable_name_to_raw_value.items():
            field_name, lookup, value = cls._parse_token(raw_token=raw_value)

            if field_name not in cls.field_name_to_field:
                raise LuceneSearchError

            variable_name_to_query_term[variable_name] = cls.field_name_to_field[field_name].get_query(field_name, lookup, value)
        return variable_name_to_query_term

    @classmethod
    def _parse_token(cls, raw_token):
        for op, lookup in EXPRESSION_OPERATOR_TO_LOOKUP.items():
            try:
                field_name, value = raw_token.split(op, 1)
                return field_name.strip(), lookup, value.strip()
            except ValueError:
                continue

        raise LuceneSearchError()


class DjangoSearchSet(LuceneToDjangoParserMixin, BaseSearchSet):
    pass
