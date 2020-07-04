import warnings
from dataclasses import dataclass
from typing import Dict, Any, Set, Optional

from lucyfer.searchset.fields import BaseSearchField, FieldType
from lucyfer.settings import lucyfer_settings


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

    field_class_for_default_searching: Optional[BaseSearchField]

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
            source_to_field_from_raw_mapping = {
                name: self.searchset_class._field_type_to_field_class.get(
                    field_type, self.searchset_class._default_field
                )(show_suggestions=name not in self.fields_to_exclude_from_suggestions, sources=[name])

                for name, field_type in self.raw_mapping.items()
            }

            # then process defined fields and its sources
            source_to_field_from_user_fields = self.field_name_to_field.copy()
            source_to_field_from_user_fields_sources = {}

            # `missed_fields` uses for process possibly missed sources from case when defined
            # some field in searchset like this one:
            # x = SearchField(sources=["y"], use_field_class_for_sources=False)
            # and when we have not found "y" in raw mapping and we have no idea what field class we need to use.
            # it will be warning in the end of function.
            missed_fields = []

            for name, field in self.field_name_to_field.items():
                if not field.sources:
                    continue

                if not field.use_field_class_for_sources:
                    # we extend missed fields by all fields because after cycle we will filter it anyway
                    missed_fields.extend([source for source in field.sources])
                    continue

                source_to_field_from_user_fields_sources.update(
                    {
                        source: field.__class__(sources=[source],
                                                show_suggestions=source not in self.fields_to_exclude_from_suggestions,
                                                get_available_values_method=field._get_available_values_method,
                                                available_values_method_kwargs=field._available_values_method_kwargs,
                                                use_cache_for_suggestions=field.use_cache_for_suggestions)
                        for source in field.sources
                    }
                )

            # now result
            # we create an empty dict and update it by our dicts with order from low to high priority.
            # it means if user have wrote field "A" in searchset and we have found field "A" in raw mapping
            # priority of searchset is higher, so in result we will see users field, not field from raw mapping.
            result = {}
            result.update(source_to_field_from_raw_mapping)
            result.update(source_to_field_from_user_fields_sources)
            result.update(source_to_field_from_user_fields)

            # and check default searching field if presented
            if self.field_class_for_default_searching:
                result.update({lucyfer_settings.FIELD_NAME_FOR_DEFAULT_SEARCH: self.field_class_for_default_searching})

            missed_fields = [field for field in missed_fields if field not in result]
            if missed_fields:
                warnings.warn(f"There is some undefined fields in {self.searchset_class}: {', '.join(missed_fields)}")

            setattr(self, "field_source_to_field_result", result)
        return self.field_source_to_field_result
