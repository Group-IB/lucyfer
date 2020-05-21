from elasticsearch_dsl import Q
from parameterized import parameterized

from lucyfer.searchset import ElasticSearchSet
from lucyfer.searchset.fields import ElasticSearchField, ElasticIntegerField, ElasticFloatField, \
    ElasticBooleanField, ElasticNullBooleanField

from tests.base import TestParsing
from tests.utils import compare_dicts, Panic, EsClient, ElasticModel


class MyElasticSearchSet(ElasticSearchSet):
    field = ElasticSearchField()
    field_with_source = ElasticSearchField(sources=["source"])
    field_with_several_sources = ElasticSearchField(sources=["source1", "source2"])

    int_field = ElasticIntegerField()
    float_field = ElasticFloatField()
    boolean_field = ElasticBooleanField()
    null_boolean_field = ElasticNullBooleanField()

    @staticmethod
    def get_es_client(**kwargs):
        return EsClient

    class Meta:
        model = ElasticModel


class TestLuceneToDjangoParsing(TestParsing):
    searchset_class = MyElasticSearchSet

    def assertQueriesEqual(self, q1, q2):
        try:
            compare_dicts(q1.to_dict(), q2.to_dict())
        except Panic:
            print(q1.to_dict())
            print(q2.to_dict())
            assert False, "queries are not equals"

    @parameterized.expand((
            (Q("term", **{"field": "value"}), ["field: value", "field:value"]),
    ))
    def test_text_values(self, expected_query, raw_expressions):
        self._check_rules(rules=raw_expressions, expected_query=expected_query)

    @parameterized.expand((
            (Q("term", **{"source": "value"}), ["field_with_source: value", ]),
            (
                    Q("term", **{"source2": "value"}) | Q("term", **{"source1": "value"}),
                    ["field_with_several_sources: value", ]
            ),
            (Q("term", **{"source2": "value"}), ["source2: value", ]),
    ))
    def test_values_with_source(self, expected_query, raw_expressions):
        self._check_rules(rules=raw_expressions, expected_query=expected_query)

    @parameterized.expand((
            (~Q("term", **{"field": "value"}), ["field! value", "field ! value"]),
            (~Q("term", **{"int_field": 1}), ["int_field ! 1"]),
            (~Q("term", **{"float_field": 1.5}), ["float_field ! 1.5"]),
            (~Q("match", **{"boolean_field": True}), ["boolean_field ! true"]),
            (~Q("match", **{"null_boolean_field": True}), ["null_boolean_field ! true"]),
    ))
    def test_negate_values(self, expected_query, raw_expressions):
        self._check_rules(rules=raw_expressions, expected_query=expected_query)

    @parameterized.expand((
            (
                    Q("match", **{"boolean_field": True}),
                    ["boolean_field : true", "boolean_field : TRUE", "boolean_field : TrUe"]
            ),
            (
                    Q("match", **{"boolean_field": False}),
                    ["boolean_field : false", "boolean_field : FALSE", "boolean_field : FaLsE"]
            ),
    ))
    def test_boolean_values(self, expected_query, raw_expressions):
        self._check_rules(rules=raw_expressions, expected_query=expected_query)

    @parameterized.expand((
            (
                    Q("match", **{"null_boolean_field": True}),
                    ["null_boolean_field : true", "null_boolean_field : TRUE", "null_boolean_field : TrUe"]
            ),
            (
                    Q("match", **{"null_boolean_field": False}),
                    ["null_boolean_field : false", "null_boolean_field : FALSE", "null_boolean_field : FaLsE"]
            ),
            (
                    Q("match", **{"null_boolean_field": None}),
                    ["null_boolean_field : null", "null_boolean_field : NULL", "null_boolean_field : NuLl"]
            ),
    ))
    def test_null_boolean_values(self, expected_query, raw_expressions):
        self._check_rules(rules=raw_expressions, expected_query=expected_query)

    @parameterized.expand((
            (
                    Q("match", **{"boolean_field": True}) | Q("term", **{"undefined_field": "ululu"}),
                    ["boolean_field : true OR undefined_field: ululu"]
            ),
            (
                    Q("term", **{"undefined_field": "ululu"}),
                    ["undefined_field: ululu"]
            ),
    ))
    def test_negate_values(self, expected_query, raw_expressions):
        self._check_rules(rules=raw_expressions, expected_query=expected_query)
