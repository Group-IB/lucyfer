from django.db.models import Q
from parameterized import parameterized

from src.django.fields import CharField, FloatField, BooleanField, IntegerField
from src.django.searchset import DjangoSearchSet
from tests.base import TestParsing


class UnicornSearchSet(DjangoSearchSet):
    char_field = CharField()
    integer_field = IntegerField()
    float_field = FloatField()
    boolean_field = BooleanField()
    field_with_source = CharField(source="ok_it_is_a_source")
    field_with_several_sources = CharField(sources=["source1", "source2"])
    field_with_several_sources_and_source = CharField(source="separated_source", sources=["source1", "source2"])


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
            (Q(separated_source__icontains="xxx") | Q(source2__icontains="xxx") | Q(source1__icontains="xxx"),
             ["field_with_several_sources_and_source: xxx"]),
    ))
    def test_rule_with_source(self, expected_query, raw_expressions):
        self._check_rules(rules=raw_expressions, expected_query=expected_query)

    @parameterized.expand((
            (~Q(char_field__iexact="value"), ["char_field!= value", "char_field != value"]),
            (~Q(integer_field__exact=1), ["integer_field != 1"]),
            (~Q(float_field__exact=0.5), ["float_field != 0.5"]),
            (~Q(boolean_field__exact=True), ["boolean_field != true"]),
    ))
    def test_negate_values(self, expected_query, raw_expressions):
        self._check_rules(rules=raw_expressions, expected_query=expected_query)
