from typing import List, Optional, Dict, Any, Type, Set

try:
    from django.utils.decorators import classproperty
except ImportError:
    from django.utils.functional import classproperty

from lucyfer.searchset.fields import BaseSearchField
from lucyfer.searchset.storage import SearchSetStorage
from lucyfer.searchset.utils import FieldType
from lucyfer.settings import lucyfer_settings


class BaseMetaClass:
    model = None

    show_suggestions = True
    escape_quotes_in_suggestions = True

    fields_to_exclude_from_mapping: List[str] = None
    fields_to_exclude_from_suggestions: List[str] = None

    search_fields_for_default_search: List[str] = None


class BaseSearchSetMetaClass(type):
    def __new__(mcs, name, bases, attrs):

        meta = mcs.get_meta(meta=attrs.pop("Meta", None))
        meta.search_fields_for_default_search = meta.search_fields_for_default_search or []

        searchset = super().__new__(mcs, name, bases, attrs)

        mcs.process_required_field(searchset=searchset, bases=bases)

        storage = mcs.get_storage(searchset=searchset, meta=meta, name=name, attrs=attrs, bases=bases)

        setattr(meta, "_storage", storage)
        setattr(searchset, "_meta", meta)

        return searchset

    _required_field = ["_field_base_class", "_default_field"]
    _default_reqiured_value = BaseSearchField

    @classmethod
    def process_required_field(mcs, searchset, bases):
        for name in mcs._required_field:
            if not hasattr(searchset, name) or getattr(searchset, name) == mcs._default_reqiured_value:
                value = getattr(bases[-1], name, mcs._default_reqiured_value) if bases else mcs._default_reqiured_value
                setattr(searchset, name, value)

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

        for field_name, field in field_name_to_field.items():
            field._contribute_to_class(field_name=field_name)

        fields_to_exclude_from_mapping = mcs.get_fields_to_exclude_from_mapping(
            searchset_fields_to_exclude_from_mapping=meta.fields_to_exclude_from_mapping or [],
            field_name_to_field=field_name_to_field,
        )

        fields_to_exclude_from_suggestions = mcs.get_fields_to_exclude_from_suggestions(
            searchset_fields_to_exclude_from_suggestions=meta.fields_to_exclude_from_suggestions or [],
            field_name_to_field=field_name_to_field,
        )

        field_class_for_default_searching = None
        if meta.search_fields_for_default_search:
            field_class_for_default_searching = searchset._field_class_for_default_searching(
                sources=meta.search_fields_for_default_search,
                use_field_class_for_sources=False
            )

        storage = SearchSetStorage(
            field_name_to_field=field_name_to_field,
            searchset_class=searchset,
            fields_to_exclude_from_mapping=fields_to_exclude_from_mapping,
            fields_to_exclude_from_suggestions=fields_to_exclude_from_suggestions,
            field_class_for_default_searching=field_class_for_default_searching,
        )

        bases_meta_classes = [base for base in bases
                              if hasattr(base, "_meta") and issubclass(base._meta, BaseMetaClass)]

        if bases_meta_classes:
            for base in bases_meta_classes:
                storage.field_name_to_field.update(
                    {
                        name: field if field.__class__ != base._default_field else searchset._default_field()
                        for name, field in base._meta._storage.field_name_to_field.items()
                    }
                )

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

    # field for default searching (without lucene-like syntax usage like `?search=ululu`)
    _field_class_for_default_searching = BaseSearchField

    # provides possibility to use auto cast for boolean/integer/etc fields by field classes usage
    # that means we analyze elastic mapping data types or django models to match it to field classes
    # TODO property
    _field_type_to_field_class: Optional[Dict[int, _field_base_class]] = None
    _raw_type_to_field_type: Optional[Dict[Any, int]] = None

    @classproperty
    def storage(cls):
        return cls._meta._storage

    @classmethod
    def get_fields_values(
            cls,
            qs,
            field_name,
            prefix='',
            cache_key="DEFAULT_KEY",
            max_return_suggestions_count=lucyfer_settings.CACHE_MAX_VALUES_COUNT_FOR_ONE_PREFIX,
            allow_empty_values=lucyfer_settings.ALLOW_EMPTY_SUGGESTIONS,
            sort_values=True,
    ) -> List[str]:
        """
        Returns search helpers for field by prefix.

        :param qs: queryset with additional filters or els search
        :param field_name: field name for get values
        :param prefix: prefix for searching values
        :param cache_key: additional argument to use possibility to cache different values for different users for ex.
        :param max_return_suggestions_count: by default is 10 but if you want more - you can change it
        :param allow_empty_values: if False you will miss empty values
        :params sort_values: sort option

        :return: list of values
        """
        if not cls._meta.show_suggestions:
            return list()

        field = cls.storage.field_source_to_field.get(field_name, cls._default_field())

        return field.get_values(
            qs=qs,
            prefix=prefix,
            cache_key=cache_key,
            model_name=cls._meta.model.__name__,
            escape_quotes_in_suggestions=cls._meta.escape_quotes_in_suggestions,
            max_return_suggestions_count=max_return_suggestions_count,
            allow_empty_values=allow_empty_values,
            sort_values=sort_values,
        )

    @classmethod
    def _get_raw_mapping(cls) -> Dict[str, FieldType]:
        """
        That method allows to get mapping in raw format. It have to be reimplemented
        """
        raise NotImplementedError()

    @classmethod
    def get_query_for_field(cls, condition):
        """
        Returns Q object with query for parsed condition
        """
        field = cls.storage.field_source_to_field.get(condition.name, cls._default_field())
        return field.get_query(condition)
