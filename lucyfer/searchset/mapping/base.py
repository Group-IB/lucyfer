from collections import OrderedDict
from typing import Type, List

from lucyfer.searchset.mapping.values.base import MappingValue


class Mapping(OrderedDict):
    """
    Mapping as a dict
    """

    _value_class: Type[MappingValue]
    _model = None

    def __init__(self, model, *args, **kwargs):
        self.model = model
        super().__init__(*args, **kwargs)

    def add_value(self, name: str,
                  use_cache_for_suggestions: bool,
                  field_type=None,
                  sources=None,
                  show_suggestions=True,
                  get_available_values_method=None,
                  escape_quotes_in_suggestions=True
                  ):
        if name not in self:
            self.update({name: self._value_class(name=name,
                                                 field_type=field_type,
                                                 sources=sources,
                                                 show_suggestions=show_suggestions,
                                                 get_available_values_method=get_available_values_method,
                                                 escape_quotes_in_suggestions=escape_quotes_in_suggestions,
                                                 use_cache_for_suggestions=use_cache_for_suggestions
                                                 )})

    def get_values(self, qs, field_name: str, prefix: str, cache_key="DEFAULT_KEY") -> List[str]:
        """
        Get values helpers for field by prefix

        :param qs: queryset with additional filters or els search
        :param field_name: field name for get values
        :param prefix: prefix for searching values
        :param cache_key: additional argument to use possibility to cache different values for different users for ex.

        :return: list of values
        """

        if field_name not in self:
            return list()

        return self[field_name].get_values(qs=qs, model_name=self.model.__name__, prefix=prefix, cache_key=cache_key)
