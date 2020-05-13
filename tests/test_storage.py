from unittest import TestCase

from lucyfer.searchset import DjangoSearchSet
from lucyfer.searchset.fields import DjangoCharField, DjangoIntegerField, DjangoFloatField, DjangoBooleanField, \
    FieldType


class Meta:
    fields = []


class EmptyModel:
    _meta = Meta()

    class objects:
        @classmethod
        def filter(cls, *args, **kwargs):
            return cls

        @classmethod
        def values_list(cls, *args, **kwargs):
            return cls

        @classmethod
        def distinct(cls):
            return []


class Model(EmptyModel):
    @classmethod
    def distinct(cls):
        return ["a", "b", "c"]


class UnicornSearchSet(DjangoSearchSet):
    char_field = DjangoCharField()
    integer_field = DjangoIntegerField()
    float_field = DjangoFloatField()
    boolean_field = DjangoBooleanField()
    field_with_source = DjangoCharField(sources=["ok_it_is_a_source"])
    field_with_several_sources = DjangoCharField(sources=["source1", "source2"])

    @classmethod
    def get_raw_mapping(cls):
        return dict()

    class Meta:
        model = Model


class TestLuceneToDjangoParsing(TestCase):
    searchset_class = UnicornSearchSet

    def test_field_name_to_field(self):
        expected_name_to_field_class = {
            'char_field': DjangoCharField, 'integer_field': DjangoIntegerField,
            'float_field': DjangoFloatField, 'boolean_field': DjangoBooleanField,
            'field_with_source': DjangoCharField, 'field_with_several_sources': DjangoCharField
        }
        for name, field in self.searchset_class.storage.field_name_to_field.items():
            self.assertEqual(expected_name_to_field_class[name], field.__class__)

        self.assertEqual(len(expected_name_to_field_class), len(self.searchset_class.storage.field_name_to_field))

    def test_fields_to_exclude_from_mapping(self):
        class SearchSet(DjangoSearchSet):
            char_field = DjangoCharField()
            integer_field = DjangoIntegerField(sources=["d", "tralala"], exclude_sources_from_mapping=False)
            float_field = DjangoFloatField(sources=["c", "ululu"], exclude_sources_from_mapping=True)

            @classmethod
            def get_raw_mapping(cls):
                return dict()

            class Meta:
                model = Model

            fields_to_exclude_from_mapping = ["a", "b"]

        expected_fields = {"a", "b", "c", "ululu"}
        self.assertEqual(len(expected_fields), len(SearchSet.storage.fields_to_exclude_from_mapping))

        for field in SearchSet.storage.fields_to_exclude_from_mapping:
            self.assertTrue(field in expected_fields, field)

    def test_fields_to_exclude_from_suggestions(self):
        class SearchSet(DjangoSearchSet):
            char_field = DjangoCharField()
            integer_field = DjangoIntegerField(sources=["d", "tralala"], exclude_sources_from_mapping=False)
            float_field = DjangoFloatField(sources=["c", "ululu"], exclude_sources_from_mapping=True,
                                           show_suggestions=False)

            @classmethod
            def get_raw_mapping(cls):
                return dict()

            class Meta:
                model = Model

            fields_to_exclude_from_suggestions = ["a", "b"]

        expected_fields = {"a", "b", "float_field"}
        self.assertEqual(len(expected_fields), len(SearchSet.storage.fields_to_exclude_from_suggestions))

        for field in SearchSet.storage.fields_to_exclude_from_suggestions:
            self.assertTrue(field in expected_fields, field)

    def test_searchset_field(self):
        self.assertEqual(self.searchset_class.storage.searchset_class, self.searchset_class)

    def test_raw_mapping(self):
        expected_mapping = dict(x=None, z=None)

        class SearchSet(DjangoSearchSet):
            @classmethod
            def _get_raw_mapping(cls):
                return expected_mapping

            class Meta:
                model = Model

        self.assertEqual(SearchSet.storage.raw_mapping, expected_mapping)

    def test_field_source_to_field(self):
        class SearchSet(DjangoSearchSet):
            char_field = DjangoCharField()
            integer_field = DjangoIntegerField(sources=["d", "tralala"], exclude_sources_from_mapping=False)
            float_field = DjangoFloatField(sources=["c", "ululu"], exclude_sources_from_mapping=True,
                                           show_suggestions=False)

            @classmethod
            def _get_raw_mapping(cls):
                return {"x": None, "y": FieldType.BOOLEAN}

            class Meta:
                model = Model

            fields_to_exclude_from_mapping = ["x"]
            fields_to_exclude_from_suggestions = ["a", "b"]

        expected_result = {
            "char_field": DjangoCharField,
            "integer_field": DjangoIntegerField,
            "d": DjangoIntegerField,
            "tralala": DjangoIntegerField,
            "float_field": DjangoFloatField,
            "c": DjangoFloatField,
            "ululu": DjangoFloatField,
            "x": SearchSet._default_field,
            "y": DjangoBooleanField
        }

        self.assertEqual(len(expected_result), len(SearchSet.storage.field_source_to_field),
                         SearchSet.storage.field_source_to_field)

        for name, field in SearchSet.storage.field_source_to_field.items():
            self.assertEqual(expected_result[name], field.__class__)

    def test_get_fields_sources(self):
        class SearchSet(DjangoSearchSet):
            char_field = DjangoCharField()
            integer_field = DjangoIntegerField(sources=["d", "tralala"])

            @classmethod
            def _get_raw_mapping(cls):
                return {"x": None, "y": FieldType.BOOLEAN}

            class Meta:
                model = Model

        expected_result = ["char_field", "d", "tralala"]
        self.assertEqual(len(expected_result), len(SearchSet.get_fields_sources()))

        for source in SearchSet.get_fields_sources():
            self.assertTrue(source in expected_result)
