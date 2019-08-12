from unittest import TestCase

from django.db.models import Q
from parameterized import parameterized

from src.django.fields import CharField, FloatField, BooleanField, IntegerField
from src.django.searchset import DjangoSearchSet


class UnicornSearchSet(DjangoSearchSet):
    char_field = CharField()
    integer_field = IntegerField()
    float_field = FloatField()
    boolean_field = BooleanField()
    field_with_source = CharField(source="ok_it_is_a_source")


class TestLuceneToDjangoParsing(TestCase):
    def _check_rule(self, rule, expected_query):
        self.assertEqual(expected_query, UnicornSearchSet.parse(raw_expression=rule))

    def _check_rules(self, rules, expected_query):
        for rule in rules:
            self._check_rule(rule=rule, expected_query=expected_query)

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

    @parameterized.expand(
        ((Q(char_field__icontains="aaa_aaa"), ["((((char_field: aaa_aaa))))", "((char_field: aaa_aaa))", ]),
         ))
    def test_several_dashes_rules(self, expected_query, raw_expressions):
        self._check_rules(rules=raw_expressions, expected_query=expected_query)

    @parameterized.expand(((Q(ok_it_is_a_source__icontains="xxx"), ["field_with_source: xxx"]), ))
    def test_rule_with_source(self, expected_query, raw_expressions):
        self._check_rules(rules=raw_expressions, expected_query=expected_query)
