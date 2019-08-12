from django.db.models import Q
from lucyparser.tree import Operator

from src.base.fields import BaseSearchField
from src.utils import LuceneSearchCastValueException


class DjangoSearchField(BaseSearchField):
    OPERATOR_TO_LOOKUP = dict()

    def get_query_by_condition(self, condition):
        if self.match_all(value=condition.value):
            return Q()

        return Q(**{"{}__{}".format(self.get_source(condition.name),
                                    self.get_operator_by_lookup(condition.operator)): self.cast_value(condition.value)})

    def match_all(self, value):
        return value == "*"

    def cast_value(self, value):
        return value

    def get_operator_by_lookup(self, operator):
        lookup = self.OPERATOR_TO_LOOKUP.get(operator)

        if lookup is None:
            # TODO ANN norm exceptions
            raise Exception()

        return lookup


class CharField(DjangoSearchField):
    OPERATOR_TO_LOOKUP = {
        Operator.EQ: "icontains",
    }

    def get_query_by_condition(self, condition):
        if self.match_all(value=condition.value):
            return Q()

        source = self.get_source(condition.name)
        wildcard_parts = self.cast_value(condition.value).split("*")

        parts_count = len(wildcard_parts)

        if parts_count == 1:
            return Q(**{"{}__{}".format(source, self.get_operator_by_lookup(condition.operator)): wildcard_parts[0]})

        query = Q()
        for index, w_part in enumerate(wildcard_parts):
            if w_part:
                if index == 0:
                    query = query & Q(**{"{}__{}".format(source, "istartswith"): w_part})
                    continue

                elif index == (parts_count - 1):
                    query = query & Q(**{"{}__{}".format(source, "iendswith"): w_part})
                    continue

                else:
                    query = query & Q(**{"{}__{}".format(source, "icontains"): w_part})
                    continue

        return query

    def cast_value(self, value):
        return value.strip().strip('\"').strip("\'")


class NumberField(DjangoSearchField):
    OPERATOR_TO_LOOKUP = {
        Operator.GTE: "gte",
        Operator.LTE: "lte",
        Operator.GT: "gt",
        Operator.LT: "lt",
        Operator.EQ: "exact",
    }


class IntegerField(NumberField):
    def cast_value(self, value):
        try:
            return int(value)
        except (ValueError, TypeError):
            raise LuceneSearchCastValueException()


class FloatField(NumberField):
    def cast_value(self, value):
        try:
            return float(value)
        except (ValueError, TypeError):
            raise LuceneSearchCastValueException()


class BooleanField(DjangoSearchField):
    OPERATOR_TO_LOOKUP = {
        Operator.EQ: "exact",
    }

    _values = {"true": True, "false": False}

    def cast_value(self, value):
        value = value.lower()
        if value in self._values:
            return self._values[value]

        raise LuceneSearchCastValueException()


class NullBooleanField(BooleanField):
    _values = {"true": True, "false": False, "null": None}
