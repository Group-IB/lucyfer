from unittest import TestCase

from django.db.models import Q
from parameterized import parameterized

from src.django.fields import CharField, FloatField, BooleanField, IntegerField
from src.django.searchhelper import DjangoSearchHelperMixin
from src.django.searchset import DjangoSearchSet
from tests.base import TestParsing


class UnicornSearchSet(DjangoSearchSet):
    char_field = CharField()
    integer_field = IntegerField()
    float_field = FloatField()
    boolean_field = BooleanField()
    field_with_source = CharField(sources=["ok_it_is_a_source"])
    field_with_several_sources = CharField(sources=["source1", "source2"])


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
                           (Q(char_field__icontains="s.om.e-") & Q(char_field__iendswith="fancy_string?"),
                            ["char_field:*s.om.e-*fancy_string?"]),
                           ))
    def test_string_wo_quotes(self, expected_query, raw_expressions):
        self._check_rules(rules=raw_expressions, expected_query=expected_query)

    @parameterized.expand(((Q(char_field__icontains="aaa_aaa"), ['char_field:   "aaa_aaa"']),
                           (Q(char_field__icontains="spaces :    heeeeree"), ['char_field:   "spaces :    heeeeree"']),
                           (Q(char_field__icontains="s.om.e-") & Q(char_field__iendswith="fancy_string?"),
                            ['char_field:"*s.om.e-*fancy_string?"']),
                           ))
    def test_string_w_double_quotes(self, expected_query, raw_expressions):
        self._check_rules(rules=raw_expressions, expected_query=expected_query)

    @parameterized.expand(((Q(char_field__icontains="aaa_aaa"), ["char_field:   'aaa_aaa'"]),
                           (Q(char_field__icontains="spaces :    heeeeree"), ["char_field:   'spaces :    heeeeree'"]),
                           (Q(char_field__icontains="s.om.e-") & Q(char_field__iendswith="fancy_string?"),
                            ["char_field:'*s.om.e-*fancy_string?'"]),
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
            (~Q(char_field__iexact="value"), ["char_field!= value", "char_field ! value"]),
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
    def test_negate_values(self, expected_query, raw_expressions):
        self._check_rules(rules=raw_expressions, expected_query=expected_query)


class TestMapping(TestCase):
    def test_not_excluding_any_fields(self):
        class NotExcludingFieldsSearchSet(DjangoSearchHelperMixin, DjangoSearchSet):
            a = CharField()
            b = FloatField(sources=["c"])

            @classmethod
            def _get_raw_mapping(cls):
                return list()

            class Meta:
                model = None

        mapping = NotExcludingFieldsSearchSet.get_mapping()
        self.assertSequenceEqual(list(mapping), ["a", "b", "c"])

    def test_exclude_fields_in_searchset_class(self):
        class ExcludeFieldsInClassSearchSet(DjangoSearchHelperMixin, DjangoSearchSet):
            a = CharField()
            b = FloatField(sources=["c"])

            fields_to_exclude_from_mapping = ["b"]

            @classmethod
            def _get_raw_mapping(cls):
                return list()

            class Meta:
                model = None

        mapping = ExcludeFieldsInClassSearchSet.get_mapping()
        self.assertSequenceEqual(list(mapping), ["a", "c"])

    def test_exclude_sources_in_field(self):
        class ExcludeSourcesInFieldsSearchSet(DjangoSearchHelperMixin, DjangoSearchSet):
            a = CharField()
            b = FloatField(sources=["c"], exclude_sources_from_mapping=True)

            @classmethod
            def _get_raw_mapping(cls):
                return list()

            class Meta:
                model = None

        mapping = ExcludeSourcesInFieldsSearchSet.get_mapping()
        self.assertSequenceEqual(list(mapping), ["a", "b"])


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


class TestSearchHelpers(TestCase):
    def test_get_available_method(self):
        class MySearchSet(DjangoSearchHelperMixin, DjangoSearchSet):
            a = CharField(get_available_values_method=lambda: ["b", "c"])

            @classmethod
            def _get_raw_mapping(cls):
                return list()

            class Meta:
                model = Model

        self.assertEqual(sorted(["b", "c"]), sorted(MySearchSet.get_fields_values(field_name="a", prefix="")))
