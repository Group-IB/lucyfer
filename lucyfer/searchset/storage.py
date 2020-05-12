from dataclasses import dataclass
from typing import Dict, Any

from lucyfer.searchset.fields import BaseSearchField


@dataclass
class SearchSetStorage:
    """
    Class provides availability to use fields in SearchSet class
    """

    searchset_class: Any

    # fields defined in searchset class and those instances
    field_name_to_field: Dict[str, BaseSearchField]

    _raw_mapping = None

    @property
    def raw_mapping(self):
        if self._raw_mapping is None:
            self._raw_mapping = self.searchset_class._get_raw_mapping()
        return self._raw_mapping

    # auto generated fields by type checking in raw mapping and sources handling in defined fields
    _field_source_to_field: Dict[str, BaseSearchField] = None

    @property
    def field_source_to_field(self) -> Dict[str, BaseSearchField]:
        if self._field_source_to_field is None:

            # first process raw mapping
            self._field_source_to_field = {
                name: self.searchset_class._field_type_to_field_class[field_type]()
                for name, field_type in self.raw_mapping.items()
                if field_type in self.searchset_class._field_type_to_field_class
            }

            # then extend it by defined fields with sources
            for name, field in self.field_name_to_field.items():
                if field.use_field_class_for_sources and not field.exclude_sources_from_mapping and field.sources:
                    self._field_source_to_field.update(
                        {
                            field_source: field
                            for field_source in field.sources
                        }
                    )
        return self._field_source_to_field
