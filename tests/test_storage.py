from unittest import TestCase, mock

from lucyfer.searchset import DjangoSearchSet
from lucyfer.searchset.fields import DjangoCharField, DjangoIntegerField, DjangoFloatField, DjangoBooleanField, \
    FieldType
from tests.utils import EmptyDjangoModel, ElasticModel, DjangoModel


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
        model = ElasticModel


class TestStorage(TestCase):
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
                model = ElasticModel

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
                model = ElasticModel

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
                model = ElasticModel

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
                model = ElasticModel

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
                model = ElasticModel

        expected_result = ["char_field", "d", "tralala"]
        self.assertEqual(len(expected_result), len(SearchSet.get_fields_sources()))

        for source in SearchSet.get_fields_sources():
            self.assertTrue(source in expected_result)

    def test_show_suggestion_for_raw_mapping_field(self):
        class SearchSet(DjangoSearchSet):
            @classmethod
            def _get_raw_mapping(cls):
                return {"x": None, "y": None}

            class Meta:
                model = EmptyDjangoModel
                fields_to_exclude_from_suggestions = ["x"]

        self.assertTrue(SearchSet.storage.field_source_to_field["y"].show_suggestions)
        self.assertFalse(SearchSet.storage.field_source_to_field["x"].show_suggestions)

    def test_not_excluding_any_fields(self):
        class NotExcludingFieldsSearchSet(DjangoSearchSet):
            a = DjangoCharField()
            b = DjangoFloatField(sources=["c"])

            @classmethod
            def _get_raw_mapping(cls):
                return dict()

            class Meta:
                model = None

        mapping = list(NotExcludingFieldsSearchSet.storage.mapping.keys())
        self.assertSequenceEqual(mapping, ["a", "b", "c"])

    def test_exclude_fields_in_searchset_class(self):
        class ExcludeFieldsInClassSearchSet(DjangoSearchSet):
            a = DjangoCharField()
            b = DjangoFloatField(sources=["c"])

            @classmethod
            def _get_raw_mapping(cls):
                return dict()

            class Meta:
                model = None
                fields_to_exclude_from_mapping = ["b"]

        mapping = list(ExcludeFieldsInClassSearchSet.storage.mapping.keys())
        self.assertSequenceEqual(list(mapping), ["a", "c"])

    def test_exclude_sources_in_field(self):
        class ExcludeSourcesInFieldsSearchSet(DjangoSearchSet):
            a = DjangoCharField()
            b = DjangoFloatField(sources=["c"], exclude_sources_from_mapping=True)

            @classmethod
            def _get_raw_mapping(cls):
                return dict()

            class Meta:
                model = None

        mapping = list(ExcludeSourcesInFieldsSearchSet.storage.mapping.keys())
        self.assertSequenceEqual(list(mapping), ["a", "b"])


class TestSearchHelpers(TestCase):
    django_mapping_get_values = "lucyfer.searchset.fields.mapping.django.DjangoMappingMixin._get_values"

    def test_get_fields_values(self):
        class MySearchSet(DjangoSearchSet):
            a = DjangoCharField()

            @classmethod
            def get_raw_mapping(cls):
                return dict()

            class Meta:
                model = DjangoModel

        expected_values = sorted(["b", "c", "bb", "bba"])

        with mock.patch(self.django_mapping_get_values, return_value=expected_values):
            self.assertEqual(expected_values, sorted(MySearchSet.get_fields_values(qs=DjangoModel.objects,
                                                                                   field_name="a",
                                                                                   prefix="")))

            self.assertEqual(expected_values, sorted(MySearchSet.get_fields_values(qs=DjangoModel.objects, field_name="a",
                                                                                   prefix="", cache_key="x")))

    def test_show_suggestions(self):
        class MySearchSet(DjangoSearchSet):
            a = DjangoCharField()

            @classmethod
            def get_raw_mapping(cls):
                return dict()

            class Meta:
                model = DjangoModel
                fields_to_exclude_from_suggestions = ["a"]

        self.assertEqual(list(), MySearchSet.get_fields_values(qs=DjangoModel.objects, field_name="a", prefix=""))

        class MyNewSearchSet(MySearchSet):
            a = DjangoCharField(show_suggestions=False)

            class Meta:
                model = EmptyDjangoModel

        self.assertEqual(list(), MyNewSearchSet.get_fields_values(qs=DjangoModel.objects, field_name="a", prefix=""))

    def test_get_available_values(self):
        def expected_available_values():
            return ['ululu', "xxxx"]

        class MySearchSet(DjangoSearchSet):
            a = DjangoCharField(get_available_values_method=expected_available_values)
            b = DjangoBooleanField()

            @classmethod
            def get_raw_mapping(cls):
                return {k: None for k in ["c", "d"]}

            class Meta:
                model = DjangoModel

        self.assertEqual(['ululu', "xxxx"], MySearchSet.get_fields_values(qs=DjangoModel.objects, field_name="a"))
        self.assertEqual(['true', 'false'], list(MySearchSet.get_fields_values(qs=DjangoModel.objects, field_name="b")))

    def test_escape_quotes(self):
        not_escaped_available_a_values = ["xxx ' xxx", 'xxx " xxx']
        escaped_available_a_values = ["xxx \\' xxx", 'xxx \\" xxx']

        class MySearchSet(DjangoSearchSet):
            a = DjangoCharField(get_available_values_method=lambda *args: not_escaped_available_a_values)

            @classmethod
            def get_raw_mapping(cls):
                return dict()

            class Meta:
                model = DjangoModel
                escape_quotes_in_suggestions = True

        self.assertEqual(escaped_available_a_values,
                         MySearchSet.get_fields_values(qs=DjangoModel.objects, field_name="a", prefix=""))

        class MySearchSet(DjangoSearchSet):
            a = DjangoCharField(get_available_values_method=lambda *args: not_escaped_available_a_values)

            @classmethod
            def get_raw_mapping(cls):
                return dict()

            class Meta:
                model = DjangoModel
                escape_quotes_in_suggestions = False

        self.assertEqual(not_escaped_available_a_values,
                         MySearchSet.get_fields_values(qs=DjangoModel.objects, field_name="a", prefix=""))
