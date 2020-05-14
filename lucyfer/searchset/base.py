from typing import List, Optional, Dict, Any, Type, Set
import warnings

from django.utils.decorators import classproperty

from lucyfer.searchset.fields import BaseSearchField
from lucyfer.searchset.storage import SearchSetStorage
from lucyfer.searchset.utils import FieldType


class BaseMetaClass:
    model = None

    show_suggestions = True
    escape_quotes_in_suggestions = True

    fields_to_exclude_from_mapping: List[str] = None
    fields_to_exclude_from_suggestions: List[str] = None


class BaseSearchSetMetaClass(type):
    def __new__(mcs, name, bases, attrs):

        meta = mcs.get_meta(meta=attrs.pop("Meta", None))

        searchset = super().__new__(mcs, name, bases, attrs)
        mcs.fill_missed_fields_for_mixins(searchset=searchset)

        storage = mcs.get_storage(searchset=searchset, meta=meta, name=name, attrs=attrs, bases=bases)

        setattr(meta, "_storage", storage)
        setattr(searchset, "_meta", meta)

        return searchset

    @classmethod
    def fill_missed_fields_for_mixins(mcs, searchset):
        for name in ["_field_base_class", "_default_field"]:
            if not hasattr(searchset, name):
                setattr(searchset, name, BaseSearchField)

    @classmethod
    def get_meta(mcs, meta) -> Type[BaseMetaClass]:
        if meta:
            class CurrentMeta(meta, BaseMetaClass):
                pass
        else:
            class CurrentMeta(BaseMetaClass):
                pass

        return CurrentMeta

    @classmethod
    def get_storage(mcs, searchset, meta, name, attrs, bases):
        field_name_to_field = mcs.get_field_name_to_field(base_field_class=searchset._field_base_class, attrs=attrs)
        mcs.validate_field_name_to_field(field_name_to_field=field_name_to_field, searchset_name=name)

        # todo remove in 0.4.0
        original_fields_to_exclude_from_mapping = \
            getattr(searchset, "fields_to_exclude_from_mapping", None) or meta.fields_to_exclude_from_mapping or []

        fields_to_exclude_from_mapping = mcs.get_fields_to_exclude_from_mapping(
            searchset_fields_to_exclude_from_mapping=original_fields_to_exclude_from_mapping,
            field_name_to_field=field_name_to_field,
        )

        # todo remove in 0.4.0
        original_fields_to_exclude_from_suggestions = \
            getattr(searchset, "fields_to_exclude_from_suggestions",
                    None) or meta.fields_to_exclude_from_suggestions or []

        fields_to_exclude_from_suggestions = mcs.get_fields_to_exclude_from_suggestions(
            searchset_fields_to_exclude_from_suggestions=original_fields_to_exclude_from_suggestions,
            field_name_to_field=field_name_to_field,
        )

        storage = SearchSetStorage(
            field_name_to_field=field_name_to_field,
            searchset_class=searchset,
            fields_to_exclude_from_mapping=fields_to_exclude_from_mapping,
            fields_to_exclude_from_suggestions=fields_to_exclude_from_suggestions,
        )

        bases_meta_classes = [base for base in bases
                              if hasattr(base, "_meta") and issubclass(base._meta, BaseMetaClass)]

        if bases_meta_classes:
            for base in bases_meta_classes:
                storage.field_name_to_field.update(base._meta._storage.field_name_to_field)

        return storage

    @classmethod
    def get_field_name_to_field(mcs,
                                base_field_class: Type[BaseSearchField],
                                attrs: Dict[str, Any],
                                ) -> Dict[str, BaseSearchField]:
        """
        Returns dictionary with fields defined in searchset (field name: field instance)

        :param base_field_class: all fields must be inheritors of that class
        :param attrs: searchset class attributes
        """
        return {name: instance for name, instance in attrs.items() if isinstance(instance, base_field_class)}

    @classmethod
    def validate_field_name_to_field(mcs,
                                     field_name_to_field: Dict[str, BaseSearchField],
                                     searchset_name: str) -> None:
        for name, field in field_name_to_field.items():
            if field.sources and len(field.sources) == 1:
                assert field.sources[0] != name, \
                    f"Defining field source equals to field name in searchset doesn't make sense. " \
                    f"You have to remove sources from field '{name}' in {searchset_name}"

    @classmethod
    def get_fields_to_exclude_from_mapping(mcs,
                                           searchset_fields_to_exclude_from_mapping: List[str],
                                           field_name_to_field: Dict[str, BaseSearchField]) -> Set[str]:
        for name, field in field_name_to_field.items():
            if field.exclude_sources_from_mapping:
                searchset_fields_to_exclude_from_mapping.extend(field.sources)
        return set(searchset_fields_to_exclude_from_mapping)

    @classmethod
    def get_fields_to_exclude_from_suggestions(mcs,
                                               searchset_fields_to_exclude_from_suggestions: List[str],
                                               field_name_to_field: Dict[str, BaseSearchField]) -> Set[str]:
        searchset_fields_to_exclude_from_suggestions.extend(
            [name for name, field in field_name_to_field.items() if not field.show_suggestions]
        )
        return set(searchset_fields_to_exclude_from_suggestions)


class BaseSearchSet(metaclass=BaseSearchSetMetaClass):
    _field_base_class = BaseSearchField

    # default field uses for creating query for fields not defined in searchset class
    _default_field = BaseSearchField

    # provides possibility to use auto cast for boolean/integer/etc fields by field classes usage
    # that means we analyze elastic mapping data types or django models to match it to field classes
    # TODO property
    _field_type_to_field_class: Optional[Dict[int, _field_base_class]] = None
    _raw_type_to_field_type: Optional[Dict[Any, int]] = None

    @classproperty
    def storage(cls):
        return cls._meta._storage

    @classproperty
    def fields_to_exclude_from_mapping(cls) -> Optional[List[str]]:
        warnings.warn("Deprected! Use cls._meta.fields_to_exclude_from_mapping instead")
        return cls._meta.fields_to_exclude_from_mapping

    @classproperty
    def fields_to_exclude_from_suggestions(cls) -> Optional[List[str]]:
        warnings.warn("Deprected! Use cls._meta.fields_to_exclude_from_suggestions instead")
        return cls._meta.fields_to_exclude_from_suggestions

    @classproperty
    def show_suggestions(cls) -> bool:
        warnings.warn("Deprected! Use cls._meta.show_suggestions instead")
        return cls._meta.show_suggestions

    @classproperty
    def escape_quotes_in_suggestions(cls) -> bool:
        warnings.warn("Deprected! Use cls._meta.escape_quotes_in_suggestions instead")
        return cls._meta.escape_quotes_in_suggestions

    @classproperty
    def _field_source_to_search_field_instance(cls):
        warnings.warn("Field will be deprecated soon. Use cls.storage.field_source_to_field instead")
        return cls.storage.field_source_to_field

    @classmethod
    def get_fields_values(cls, qs, field_name, prefix='', cache_key="DEFAULT_KEY") -> List[str]:
        """
        Returns search helpers for field by prefix.

        :param qs: queryset with additional filters or els search
        :param field_name: field name for get values
        :param prefix: prefix for searching values
        :param cache_key: additional argument to use possibility to cache different values for different users for ex.

        :return: list of values
        """
        if not cls._meta.show_suggestions:
            return list()

        return cls.storage.field_source_to_field.get(field_name, cls._default_field()).get_values(
            qs=qs, prefix=prefix, cache_key=cache_key, model_name=cls._meta.model.__name__,
            escape_quotes_in_suggestions=cls._meta.escape_quotes_in_suggestions
        )

    @classmethod
    def get_fields_to_exclude_from_mapping(cls) -> Set[str]:
        warnings.warn("Deprecated! Use cls.storage.fields_to_exclude_from_mapping instead")
        return cls.storage.fields_to_exclude_from_mapping

    @classmethod
    def get_fields_to_exclude_from_suggestions(cls) -> Set[str]:
        warnings.warn("Deprecated! Use cls.storage.fields_to_exclude_from_suggestions instead")
        return cls.storage.fields_to_exclude_from_suggestions

    @classmethod
    def get_raw_mapping(cls) -> Dict[str, Optional[FieldType]]:
        warnings.warn("Method will be deprecated soon. Use cls.storage.raw_mapping instead")
        return cls.storage.raw_mapping

    @classmethod
    def get_full_mapping(cls):
        warnings.warn("Method will be deprecated soon. Use cls.storage.mapping instead")
        return cls.storage.mapping

    @classmethod
    def _get_raw_mapping(cls) -> Dict[str, FieldType]:
        """
        That method allows to get mapping in raw format. It have to be reimplemented
        """
        raise NotImplementedError()

    @classmethod
    def get_field_name_to_field(cls):
        """
        Returns dictionary with fieldnames defined in searchset class and field instances
        """
        warnings.warn("Method will be deprecated soon. Use cls.storage.field_name_to_field instead")
        return cls.storage.field_name_to_field

    @classmethod
    def get_query_for_field(cls, condition):
        """
        Returns Q object with query for parsed condition
        """
        field = cls.storage.field_source_to_field.get(condition.name, cls._default_field())
        return field.get_query(condition)
