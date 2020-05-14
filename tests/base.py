from unittest import TestCase


class TestParsing(TestCase):
    def _check_rule(self, rule, expected_query):
        self.assertQueriesEqual(expected_query, self.searchset_class.parse(raw_expression=rule))

    def _check_rules(self, rules, expected_query):
        for rule in rules:
            self._check_rule(rule=rule, expected_query=expected_query)
