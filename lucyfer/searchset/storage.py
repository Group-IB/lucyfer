import warnings
from dataclasses import dataclass
from typing import Dict, Any, Set

from lucyfer.searchset.fields import BaseSearchField, FieldType


@dataclass
class SearchSetStorage:
    """
    Class provides availability to use fields in SearchSet class
    """

    searchset_class: Any

    # fields defined in searchset class and those instances
    field_name_to_field: Dict[str, BaseSearchField]

    fields_to_exclude_from_mapping: Set[str]
    fields_to_exclude_from_suggestions: Set[str]

    _full_mapping = None

    @property
    def mapping(self):
        """
        Returns mapping for current searchset. Its looks like {field name: field}
        That property only contains fields not excluded from original mapping
        If you want to get values for some field in mapping - don't. You better use `field_source_to_field`
        """
        return {
            name: field for name, field in self.field_source_to_field.items()
            if name not in self.fields_to_exclude_from_mapping
        }

    @property
    def raw_mapping(self) -> Dict[str, FieldType]:
        """
        Caches raw mapping and return it
        """
        if not hasattr(self, 'raw_mapping_result'):
            result = self.searchset_class._get_raw_mapping()
            setattr(self, 'raw_mapping_result', result)
        return self.raw_mapping_result

    @property
    def field_source_to_field(self) -> Dict[str, BaseSearchField]:
        """
        Auto generated fields by type checking in raw mapping and sources handling in defined fields
        """
        if not hasattr(self, 'field_source_to_field_result'):
            # first process raw mapping
            result = {
                name: self.searchset_class._field_type_to_field_class.get(
                    field_type, self.searchset_class._default_field
                )()
                for name, field_type in self.raw_mapping.items()
            }

            # if some fields user has use in sources with use_field_class_for_sources=False
            # and we can't find this fields in raw mapping
            # they will be here with warning
            missed_fields = []

            # then extend it by defined fields with sources
            for name, field in self.field_name_to_field.items():
                result[name] = field

                if field.sources:
                    if field.use_field_class_for_sources:
                        result.update(
                            {
                                field_source: field
                                for field_source in field.sources
                            }
                        )
                    else:
                        missed_fields.extend([source for source in field.sources if source not in result])

                if field.use_field_class_for_sources and field.sources:
                    result.update(
                        {
                            field_source: field
                            for field_source in field.sources
                        }
                    )
            # now process the sources
            missed_fields = [field for field in missed_fields if field not in result]
            if missed_fields:
                warnings.warn(f"There is some undefined fields in {self.searchset_class}: {', '.join(missed_fields)}")

            setattr(self, "field_source_to_field_result", result)
        return self.field_source_to_field_result
