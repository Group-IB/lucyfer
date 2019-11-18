from unittest import TestCase

from django.conf import settings


class LucyferTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not settings.configured:
            settings.configure()


class TestParsing(LucyferTestCase):
    def _check_rule(self, rule, expected_query):
        self.assertQueriesEqual(expected_query, self.searchset_class.parse(raw_expression=rule))

    def _check_rules(self, rules, expected_query):
        for rule in rules:
            self._check_rule(rule=rule, expected_query=expected_query)
