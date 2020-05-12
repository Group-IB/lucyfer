from unittest import mock

from django.db.models import Q
from parameterized import parameterized

from lucyfer.searchset import DjangoSearchSet
from lucyfer.searchset.fields import DjangoCharField, DjangoIntegerField, DjangoFloatField, DjangoBooleanField
from tests.base import TestParsing, LucyferTestCase


class Model:
    class objects:
        @classmethod
        def filter(cls, *args, **kwargs):
            return cls

        @classmethod
        def values_list(cls, *args, **kwargs):
            return cls

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


class TestLuceneToDjangoParsing(TestParsing):
    searchset_class = UnicornSearchSet

    def assertQueriesEqual(self, q1, q2):
        assert q1.__class__ == q2.__class__
        assert (q1.connector, q1.negated) == (q2.connector, q2.negated)
        assert sorted(q1.children) == sorted(q2.children)

    @parameterized.expand(((Q(boolean_field__exact=True),
                            ["boolean_field: true", "boolean_field:TRUE", "boolean_field: tRuE"]),
                           (Q(boolean_field__exact=False),
                            ["boolean_field: false", "boolean_field:FALSE", "boolean_field: FaLsE"]),
                           ))
    def test_bool_values(self, expected_query, raw_expressions):
        self._check_rules(rules=raw_expressions, expected_query=expected_query)

    @parameterized.expand(((Q(integer_field__exact=1), ["integer_field: 1", "integer_field:1"]),
                           (Q(integer_field__exact=-1), ["integer_field: -1", "integer_field:-1"]),
                           ))
    def test_integer_values(self, expected_query, raw_expressions):
        self._check_rules(rules=raw_expressions, expected_query=expected_query)

    @parameterized.expand(((Q(float_field__exact=123.153), ["float_field:  123.153"]),
                           (Q(float_field__exact=0.11), ["float_field:0.11"]),
                           (Q(float_field__exact=0.136), ["float_field:0.136"]),
                           (Q(float_field__exact=-123.153), ["float_field:  -123.153"]),
                           (Q(float_field__exact=-0.11), ["float_field:-0.11"]),
                           (Q(float_field__exact=-0.136), ["float_field:-0.136"]),
                           ))
    def test_float_values(self, expected_query, raw_expressions):
        self._check_rules(rules=raw_expressions, expected_query=expected_query)

    @parameterized.expand(((Q(char_field__icontains="aaa_aaa"), ["char_field:   aaa_aaa"]),
                           (Q(char_field__iendswith="s.om.e-*fancy_string?"), ["char_field:*s.om.e-*fancy_string?"]),
                           ))
    def test_string_wo_quotes(self, expected_query, raw_expressions):
        self._check_rules(rules=raw_expressions, expected_query=expected_query)

    @parameterized.expand(((Q(char_field__icontains="aaa_aaa"), ['char_field:   "aaa_aaa"']),
                           (Q(char_field__icontains="spaces :    heeeeree"), ['char_field:   "spaces :    heeeeree"']),
                           (Q(char_field__iendswith="s.om.e-*fancy_string?"), ['char_field:"*s.om.e-*fancy_string?"']),
                           ))
    def test_string_w_double_quotes(self, expected_query, raw_expressions):
        self._check_rules(rules=raw_expressions, expected_query=expected_query)

    @parameterized.expand(((Q(char_field__icontains="aaa_aaa"), ["char_field:   'aaa_aaa'"]),
                           (Q(char_field__icontains="spaces :    heeeeree"), ["char_field:   'spaces :    heeeeree'"]),
                           (Q(char_field__iendswith="s.om.e-*fancy_string?"), ["char_field:'*s.om.e-*fancy_string?'"]),
                           ))
    def test_string_w_single_quotes(self, expected_query, raw_expressions):
        self._check_rules(rules=raw_expressions, expected_query=expected_query)

    @parameterized.expand(((Q(char_field__icontains="aaa_aaa") | Q(integer_field__exact=5),
                            [
                                "char_field: aaa_aaa OR integer_field: 5",
                                "char_field: aaa_aaa or integer_field: 5",
                                "( char_field: aaa_aaa) OR (integer_field: 5)",
                                "(char_field: aaa_aaa )or( integer_field: 5)",
                            ]
                            ),
                           ))
    def test_rules_with_or_expression(self, expected_query, raw_expressions):
        self._check_rules(rules=raw_expressions, expected_query=expected_query)

    @parameterized.expand(((Q(char_field__icontains="aaa_aaa") & Q(integer_field__exact=5),
                            ["char_field: aaa_aaa AND integer_field: 5", "char_field: aaa_aaa and integer_field: 5",
                             "( char_field: aaa_aaa) AND (integer_field: 5)",
                             "(char_field: aaa_aaa )and( integer_field: 5)", ]),
                           ))
    def test_rules_with_and_expression(self, expected_query, raw_expressions):
        self._check_rules(rules=raw_expressions, expected_query=expected_query)

    @parameterized.expand((
            (Q(char_field__icontains="aaa_aaa"), ["((((char_field: aaa_aaa))))", "((char_field: aaa_aaa))", ]),
    ))
    def test_several_dashes_rules(self, expected_query, raw_expressions):
        self._check_rules(rules=raw_expressions, expected_query=expected_query)

    @parameterized.expand((
            (Q(ok_it_is_a_source__icontains="xxx"), ["field_with_source: xxx"]),
            (Q(source2__icontains="xxx") | Q(source1__icontains="xxx"), ["field_with_several_sources: xxx"]),
    ))
    def test_rule_with_source(self, expected_query, raw_expressions):
        self._check_rules(rules=raw_expressions, expected_query=expected_query)

    @parameterized.expand((
            (~Q(char_field__iexact="value"), ["char_field! value", "char_field ! value"]),
            (~Q(integer_field__exact=1), ["integer_field ! 1"]),
            (~Q(float_field__exact=0.5), ["float_field ! 0.5"]),
            (~Q(boolean_field__exact=True), ["boolean_field ! true"]),
    ))
    def test_negate_values(self, expected_query, raw_expressions):
        self._check_rules(rules=raw_expressions, expected_query=expected_query)

    @parameterized.expand((
            (
                    Q(boolean_field__exact=True) | Q(undefined_field__iexact="ululu"),
                    ["boolean_field : true OR undefined_field: ululu"]
            ),
            (
                    Q(undefined_field__iexact="ululu"),
                    ["undefined_field: ululu"]
            ),
    ))
    def test_undefined_values(self, expected_query, raw_expressions):
        self._check_rules(rules=raw_expressions, expected_query=expected_query)


class TestMapping(LucyferTestCase):
    def test_not_excluding_any_fields(self):
        class NotExcludingFieldsSearchSet(DjangoSearchSet):
            a = DjangoCharField()
            b = DjangoFloatField(sources=["c"])

            @classmethod
            def get_raw_mapping(cls):
                return dict()

            class Meta:
                model = None

        mapping = list(NotExcludingFieldsSearchSet.get_full_mapping().keys())
        self.assertSequenceEqual(list(mapping), ["a", "b", "c"])

    def test_exclude_fields_in_searchset_class(self):
        class ExcludeFieldsInClassSearchSet(DjangoSearchSet):
            a = DjangoCharField()
            b = DjangoFloatField(sources=["c"])

            fields_to_exclude_from_mapping = ["b"]

            @classmethod
            def get_raw_mapping(cls):
                return dict()

            class Meta:
                model = None

        mapping = list(ExcludeFieldsInClassSearchSet.get_full_mapping().keys())
        self.assertSequenceEqual(list(mapping), ["a", "c"])

    def test_exclude_sources_in_field(self):
        class ExcludeSourcesInFieldsSearchSet(DjangoSearchSet):
            a = DjangoCharField()
            b = DjangoFloatField(sources=["c"], exclude_sources_from_mapping=True)

            @classmethod
            def get_raw_mapping(cls):
                return dict()

            class Meta:
                model = None

        mapping = list(ExcludeSourcesInFieldsSearchSet.get_full_mapping().keys())
        self.assertSequenceEqual(list(mapping), ["a", "b"])


class TestSearchHelpers(LucyferTestCase):
    django_mapping_get_values = "lucyfer.searchset.mapping.DjangoMappingValue._get_values"

    def test_get_fields_values(self):
        class MySearchSet(DjangoSearchSet):
            a = DjangoCharField()

            @classmethod
            def get_raw_mapping(cls):
                return dict()

            class Meta:
                model = Model

        expected_values = sorted(["b", "c", "bb", "bba"])

        with mock.patch(self.django_mapping_get_values, return_value=expected_values):
            self.assertEqual(expected_values, sorted(MySearchSet.get_fields_values(qs=Model.objects, field_name="a",
                                                                                   prefix="")))

            self.assertEqual(expected_values, sorted(MySearchSet.get_fields_values(qs=Model.objects, field_name="a",
                                                                                   prefix="", cache_key="x")))

    def test_show_suggestions(self):
        class MySearchSet(DjangoSearchSet):
            a = DjangoCharField()

            @classmethod
            def get_raw_mapping(cls):
                return dict()

            class Meta:
                model = Model

            fields_to_exclude_from_suggestions = ["a"]

        self.assertEqual(list(), MySearchSet.get_fields_values(qs=Model.objects, field_name="a", prefix=""))

        class MyNewSearchSet(MySearchSet):
            a = DjangoCharField(show_suggestions=False)

        self.assertEqual(list(), MyNewSearchSet.get_fields_values(qs=Model.objects, field_name="a", prefix=""))

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
                model = Model

        self.assertEqual(['ululu', "xxxx"], MySearchSet.get_fields_values(qs=Model.objects, field_name="a"))
        self.assertEqual(['true', 'false'], list(MySearchSet.get_fields_values(qs=Model.objects, field_name="b")))

    def test_escape_quotes(self):
        not_escaped_available_a_values = ["xxx ' xxx", 'xxx " xxx']
        escaped_available_a_values = ["xxx \\' xxx", 'xxx \\" xxx']

        class MySearchSet(DjangoSearchSet):
            a = DjangoCharField(get_available_values_method=lambda *args: not_escaped_available_a_values)

            @classmethod
            def get_raw_mapping(cls):
                return dict()

            class Meta:
                model = Model

            escape_quotes_in_suggestions = True

        self.assertEqual(escaped_available_a_values,
                         MySearchSet.get_fields_values(qs=Model.objects, field_name="a", prefix=""))

        class MySearchSet(DjangoSearchSet):
            a = DjangoCharField(get_available_values_method=lambda *args: not_escaped_available_a_values)

            @classmethod
            def get_raw_mapping(cls):
                return dict()

            class Meta:
                model = Model

            escape_quotes_in_suggestions = False

        self.assertEqual(not_escaped_available_a_values,
                         MySearchSet.get_fields_values(qs=Model.objects, field_name="a", prefix=""))
